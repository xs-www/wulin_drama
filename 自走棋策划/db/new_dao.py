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
DB_PATH = BASE_DIR / "database.db"
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

class CharacterDao:
    """
    角色数据访问对象
    """
    def __init__(self, conn):
        self.conn = conn
        self.mapper = mapper.get("CharacterDao", {})

        self._ensure_table_exists()

    def _ensure_table_exists(self):
        """
        确保角色表存在
        """
        cursor = self.conn.cursor()
        cursor.execute(self.mapper.get("create_table_query"))
        self.conn.commit()

    def update_mapper(self):
        """
        按照mapper的fields更新 SQL 映射
        """
        fields = self.mapper.get("fields")
        create_table_query = f"""CREATE TABLE IF NOT EXISTS characters (
        {', '.join([f"{field} {props['type']}{' PRIMARY KEY' if props.get('primary_key') else ''}{' NOT NULL' if props.get('not_null') else ''}{' DEFAULT ' + str(props['default']) if props.get('default') is not None else ''}" for field, props in fields.items()])}
        );"""
        insert_query = f"""INSERT INTO characters ({', '.join(fields.keys())}) VALUES ({', '.join(['?' for _ in fields])});"""
        update_query = f"""UPDATE characters SET {', '.join([f"{field} = ?" for field in fields.keys() if field != 'id'])} WHERE id = ?;"""
        
        self.mapper["create_table_query"] = create_table_query
        self.mapper["insert_query"] = insert_query
        self.mapper["update_query"] = update_query

        mapper["CharacterDao"] = self.mapper
        save_mapper()

    def get_character_by_id(self, char_id):
        """
        根据角色ID获取角色信息
        :param char_id: 角色ID
        :return: 角色信息字典
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM characters WHERE id = ?", (char_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

if __name__ == "__main__":
    conn = connect_database()
    char_dao = CharacterDao(conn)
    char_dao.update_mapper()
    dumpSql()