"""
数据访问层 (Data Access Object)
用于管理数据库连接和执行 CRUD 操作
"""
import sqlite3
import json
import os
from pathlib import Path

# 获取当前文件所在目录
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "new_database.db"
SQL_DIR = BASE_DIR / "sql"
MAPPER_PATH = BASE_DIR / "mapper.json"

with open(MAPPER_PATH, "r", encoding="utf-8") as f:
    mapper = json.load(f)

def connect_database(db_path=None):
    """
    连接到 SQLite 数据库
    :param db_path: 数据库文件路径，默认为 database.db
    :return: 数据库连接对象
    """
    if db_path is None:
        db_path = DB_PATH
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # 使查询结果可以像字典一样访问
    return conn

def save_mapper():
    with open(MAPPER_PATH, "w", encoding="utf-8") as f:
        json.dump(mapper, f, indent=4, ensure_ascii=False)

def updateDB(db_path=None):
    """
    更新数据库结构
    :param db_path: 数据库文件路径，默认为 database.db
    """
    conn = connect_database(db_path)
    cursor = conn.cursor()

    sql_files = sorted(SQL_DIR.glob("*.sql"))
    for sql_file in sql_files:
        with open(sql_file, "r", encoding="utf-8") as f:
            sql_script = f.read()
            cursor.executescript(sql_script)
    
    conn.commit()
    conn.close()

def dumpSql(db_path=None, output_dir=None):
    """
    导出数据库为 .sql 文件到 sql 文件夹
    :param db_path: 数据库文件路径
    :param output_dir: 输出目录路径
    :return: 是否成功
    """
    if db_path is None:
        db_path = DB_PATH
    if output_dir is None:
        output_dir = SQL_DIR

    conn = connect_database(db_path)
    cursor = conn.cursor()

    sql_dump = "\n".join(conn.iterdump())

    os.makedirs(output_dir, exist_ok=True)
    output_path = Path(output_dir) / "database_dump_new.sql"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(sql_dump)

    conn.close()
    return True

def update_mapper(table_name="Character"):
    """
    按照mapper的fields更新 SQL 映射
    """
    mapper_name = f"{table_name}Dao"
    aim_mapper = mapper.get(mapper_name, {})
    fields = aim_mapper.get("fields", {})
    primary_keys = [field for field, props in fields.items() if props.get("primary_key")]
    if len(primary_keys) == 1:
        create_table_query = f"""CREATE TABLE IF NOT EXISTS {table_name} (
        {', '.join([f"{field} {props['type']}{' PRIMARY KEY' if props.get('primary_key') else ''}{' AUTOINCREMENT' if props.get('autoincrement') else ''}{' NOT NULL' if props.get('not_null') else ''}{' DEFAULT ' + str(props['default']) if props.get('default') is not None else ''}" for field, props in fields.items()])}
        );"""
        update_query = f"""UPDATE {table_name} SET 
        {', '.join([f"{field} = ?" for field in fields.keys() if field not in primary_keys])} WHERE {primary_keys[0]} = ?;"""
    else:
        create_table_query = f"""CREATE TABLE IF NOT EXISTS {table_name} (
        {', '.join([f"{field} {props['type']}{' NOT NULL' if props.get('not_null') else ''}{' DEFAULT ' + str(props['default']) if props.get('default') is not None else ''}" for field, props in fields.items()])}
        , PRIMARY KEY ({', '.join([field for field, props in fields.items() if props.get('primary_key')])})
        );"""
        update_query = f"""UPDATE {table_name} SET 
        {', '.join([f"{field} = ?" for field in fields.keys() if field not in primary_keys])} WHERE {' AND '.join([f"{field} = ?" for field in primary_keys])};"""
    insert_query = f"""INSERT INTO {table_name} ({', '.join(fields.keys())}) VALUES ({', '.join(['?' for _ in fields])});"""
    #update_query = f"""UPDATE {table_name} SET {', '.join([f"{field} = ?" for field in fields.keys() if field != 'id'])} WHERE id = ?;"""

    aim_mapper["create_table_query"] = create_table_query
    aim_mapper["insert_query"] = insert_query
    aim_mapper["update_query"] = update_query

    mapper[mapper_name] = aim_mapper
    #print("Updated mapper for", aim_mapper)
    save_mapper()

def create_table(table_name):
    """
    创建指定表
    :param table_name: 表名
    """
    conn = connect_database()
    cursor = conn.cursor()
    mapper_name = f"{table_name}Dao"
    table_mapper = mapper.get(mapper_name, {})
    cursor.execute(table_mapper.get("create_table_query"))
    conn.commit()
    conn.close()

def drop_table(table_name):
    """
    删除指定表
    :param table_name: 表名
    """
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.commit()
    conn.close()

class CharacterDao:
    """
    角色数据访问对象
    """
    def __init__(self):
        self.mapper = mapper.get("CharacterDao", {})

        update_mapper("Character")
        create_table("Character")

    def insert_column_to_mapper(self, column_name, column_info: dict):
        """
        向 mapper 中添加新列信息
        :param column_name: 列名
        :param column_info: 列信息字典
        """
        self.mapper.setdefault("fields", {})[column_name] = column_info
        update_mapper("Character")

    def delete_column_from_mapper(self, column_name):
        """
        从 mapper 中删除列信息
        :param column_name: 列名
        """
        if column_name in self.mapper.get("fields", {}):
            del self.mapper["fields"][column_name]
            update_mapper("Character")

    def get_character_count(self, conn):
        """
        获取角色总数
        :return: 角色总数
        """
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM character")
        row = cursor.fetchone()
        return row["count"] if row else 0
    
    def get_next_id(self, conn):
        """
        获取下一个可用的角色ID
        :return: 下一个角色ID
        """
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) as max_id FROM sqlite_sequence WHERE name = 'Character'")
        row = cursor.fetchone()
        return (row["max_id"] or 0) + 1

    def select_all_characters(self, conn):
        """
        获取所有角色信息
        :return: 角色信息列表
        """
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM character LEFT JOIN CharacterFetter ON character.id = CharacterFetter.character_id")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def select_character_by_id(self, char_id, conn):
        """
        根据角色ID获取角色信息
        :param char_id: 角色ID
        :return: 角色信息字典
        """
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM character WHERE id = ?", (char_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def select_character_by_price(self, price, conn):
        """
        根据价格获取角色信息
        :param price: 角色价格
        :return: 角色信息列表
        """
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM character WHERE price = ?", (price,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def insert_character(self, character_values: list, conn):
        """
        插入新角色
        :param character: 角色信息字典
        """
        cursor = conn.cursor()
        return cursor.execute(self.mapper.get("insert_query"), tuple(character_values)).lastrowid 

    def update_character(self, char_id, updates: dict, conn):
        """
        更新角色信息
        :param char_id: 角色ID
        :param updates: 更新内容字典
        """
        cursor = conn.cursor()
        cursor.execute(self.mapper.get("update_query"), (*updates.values(), char_id))

    def delete_character(self, char_id, conn):
        """
        删除角色
        :param char_id: 角色ID
        """
        cursor = conn.cursor()
        cursor.execute("DELETE FROM character WHERE id = ?", (char_id,))

    def insert_column(self, column_name, column_type, default_value=None, not_null=False, conn=None):
        """
        向角色表中添加新列
        :param column_name: 列名
        :param column_type: 列类型
        :param default_value: 默认值
        """
        cursor = conn.cursor()
        alter_query = f"ALTER TABLE character ADD COLUMN {column_name} {column_type}"
        if default_value is not None:
            alter_query += f" DEFAULT {default_value}"
        if not_null:
            alter_query += " NOT NULL"
        cursor.execute(alter_query)

    def get_related_fetters(self, char_id, conn):
        """
        根据角色ID获取关联羁绊信息
        :param char_id: 角色ID
        :return: 羁绊信息列表
        """
        cursor = conn.cursor()
        cursor.execute("""SELECT fetter.*, CharacterFetter.character_id FROM fetter
                          JOIN CharacterFetter ON fetter.id = CharacterFetter.fetter_id
                          WHERE CharacterFetter.character_id = ?""", (char_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

class FetterDao:
    """
    角色羁绊数据访问对象
    """
    def __init__(self):
        self.mapper = mapper.get("FetterDao", {})

        update_mapper("Fetter")
        create_table("Fetter")
    
    def insert_fetter(self, fetter_values: list, conn):
        """
        插入新羁绊
        :param fetter_values: 羁绊信息列表
        """
        cursor = conn.cursor()
        cursor.execute(self.mapper.get("insert_query"), tuple(fetter_values))

    def update_fetter(self, fetter_id, updates: list, conn):
        """
        更新羁绊信息
        :param fetter_id: 羁绊ID
        :param updates: 更新内容字典
        """
        cursor = conn.cursor()
        cursor.execute(self.mapper.get("update_query"), (*updates, fetter_id))

    def select_all_fetters(self, conn):
        """
        获取所有羁绊信息
        :return: 羁绊信息列表
        """
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fetter")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def select_all_fetter_id(self, conn):
        """
        获取所有羁绊ID
        :return: 羁绊ID列表
        """
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM fetter")
        rows = cursor.fetchall()
        return list(set([row["id"] for row in rows]))

    def select_fetter_by_id(self, fetter_id, conn):
        """
        根据羁绊ID获取羁绊信息
        :param fetter_id: 羁绊ID
        :return: 羁绊信息字典
        """
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fetter WHERE id = ?", (fetter_id,))
        rows = cursor.fetchall()
        if rows:
            return [dict(row) for row in rows]
        return None

    def get_ralated_characters(self, fetter_id, conn):
        """
        根据羁绊ID获取关联角色信息
        :param fetter_id: 羁绊ID
        :return: 角色信息列表
        """
        cursor = conn.cursor()
        cursor.execute("""SELECT character.*, CharacterFetter.fetter_id FROM character
                          JOIN CharacterFetter ON character.id = CharacterFetter.character_id
                          WHERE CharacterFetter.fetter_id = ?""", (fetter_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
class CharacterFetterDao:
    """
    角色羁绊关联数据访问对象
    """
    def __init__(self):
        self.mapper = mapper.get("CharacterFetterDao", {})

        update_mapper("CharacterFetter")
        create_table("CharacterFetter")

    def insert_character_fetter(self, char_fetter_values: list, conn):
        """
        插入新角色羁绊关联
        :param char_fetter_values: 角色羁绊信息列表
        """
        cursor = conn.cursor()
        cursor.execute(self.mapper.get("insert_query"), tuple(char_fetter_values))

    def delete_character_fetter_by_char_id(self, char_id, conn):
        """
        根据角色ID删除角色羁绊关联
        :param char_id: 角色ID
        """
        cursor = conn.cursor()
        cursor.execute("DELETE FROM CharacterFetter WHERE character_id = ?", (char_id,))

    def delete_character_fetter_by_fetter_id(self, fetter_id, conn):
        """
        根据羁绊ID删除角色羁绊关联
        :param fetter_id: 羁绊ID
        """
        cursor = conn.cursor()
        cursor.execute("DELETE FROM CharacterFetter WHERE fetter_id = ?", (fetter_id,))

    def get_fetters_by_char_id(self, char_id, conn):
        """
        根据角色ID获取关联羁绊信息
        :param char_id: 角色ID
        :return: 羁绊信息列表
        """
        cursor = conn.cursor()
        cursor.execute("SELECT fetter_id FROM CharacterFetter WHERE character_id = ?", (char_id,))
        rows = cursor.fetchall()
        return [dict(row).get("fetter_id") for row in rows]

if __name__ == "__main__":
    dumpSql()