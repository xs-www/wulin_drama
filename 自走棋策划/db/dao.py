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


class CharacterDao:
    """
    Character 表的数据访问对象
    提供增删查改功能
    """
    
    def __init__(self, db_path=None):
        """
        初始化 CharacterDao
        :param db_path: 数据库文件路径
        """
        self.db_path = db_path if db_path else DB_PATH
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """确保 character 表存在"""
        conn = connect_database(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS character (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                localization TEXT,
                attack_power INTEGER DEFAULT 4,
                health_points INTEGER DEFAULT 8,
                speed INTEGER DEFAULT 2,
                hate_value INTEGER DEFAULT 1,
                price INTEGER DEFAULT 1,
                weapon TEXT,
                energy INTEGER DEFAULT 0,
                avaliable_location TEXT,
                fetter TEXT,
                hate_matrix TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create(self, character_dict):
        """
        创建一个新的 character 记录
        :param character_dict: 包含 character 数据的字典
        :return: 插入的行数
        """
        conn = connect_database(self.db_path)
        cursor = conn.cursor()
        
        # 处理列表和嵌套结构，转换为 JSON 字符串
        character_dict = character_dict.copy()
        if 'avaliable_location' in character_dict and isinstance(character_dict['avaliable_location'], list):
            character_dict['avaliable_location'] = json.dumps(character_dict['avaliable_location'])
        if 'fetter' in character_dict and isinstance(character_dict['fetter'], list):
            character_dict['fetter'] = json.dumps(character_dict['fetter'])
        if 'hate_matrix' in character_dict and isinstance(character_dict['hate_matrix'], list):
            character_dict['hate_matrix'] = json.dumps(character_dict['hate_matrix'])
        
        columns = ', '.join(character_dict.keys())
        placeholders = ', '.join(['?' for _ in character_dict])
        query = f'INSERT INTO character ({columns}) VALUES ({placeholders})'
        
        cursor.execute(query, list(character_dict.values()))
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        
        return rowcount

    def get_next_id(self):
        """
        计算当前数据库中最大的数值型 id 并返回下一个 id（字符串形式）。
        非数值 id 会被忽略。
        如果表为空或没有数值 id，返回 '1'
        """
        conn = connect_database(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM character')
        rows = cursor.fetchall()
        conn.close()

        max_id = 0
        for row in rows:
            try:
                # sqlite3.Row 可通过索引或键访问
                val = row['id'] if isinstance(row, sqlite3.Row) else row[0]
                val_int = int(val)
                if val_int > max_id:
                    max_id = val_int
            except Exception:
                # 忽略无法转换为整数的 id
                continue

        return str(max_id + 1)
    
    def read(self, character_id):
        """
        根据 ID 读取一个 character 记录
        :param character_id: character 的 ID
        :return: character 字典，如果不存在则返回 None
        """
        conn = connect_database(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM character WHERE id = ?', (character_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            character_dict = dict(row)
            # 将 JSON 字符串转换回列表
            if character_dict.get('avaliable_location'):
                try:
                    character_dict['avaliable_location'] = json.loads(character_dict['avaliable_location'])
                except:
                    pass
            if character_dict.get('fetter'):
                try:
                    character_dict['fetter'] = json.loads(character_dict['fetter'])
                except:
                    pass
            if character_dict.get('hate_matrix'):
                try:
                    character_dict['hate_matrix'] = json.loads(character_dict['hate_matrix'])
                except:
                    pass
            return character_dict
        return None
    
    def read_all(self):
        """
        读取所有 character 记录
        :return: character 字典列表
        """
        conn = connect_database(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM character ORDER BY id')
        rows = cursor.fetchall()
        conn.close()
        
        characters = []
        for row in rows:
            character_dict = dict(row)
            # 将 JSON 字符串转换回列表
            if character_dict.get('avaliable_location'):
                try:
                    character_dict['avaliable_location'] = json.loads(character_dict['avaliable_location'])
                except:
                    pass
            if character_dict.get('fetter'):
                try:
                    character_dict['fetter'] = json.loads(character_dict['fetter'])
                except:
                    pass
            if character_dict.get('hate_matrix'):
                try:
                    character_dict['hate_matrix'] = json.loads(character_dict['hate_matrix'])
                except:
                    pass
            characters.append(character_dict)
        
        return characters
    
    def update(self, character_id, character_dict):
        """
        更新一个 character 记录
        :param character_id: character 的 ID
        :param character_dict: 包含更新数据的字典
        :return: 更新的行数
        """
        conn = connect_database(self.db_path)
        cursor = conn.cursor()
        
        # 处理列表和嵌套结构，转换为 JSON 字符串
        character_dict = character_dict.copy()
        if 'avaliable_location' in character_dict and isinstance(character_dict['avaliable_location'], list):
            character_dict['avaliable_location'] = json.dumps(character_dict['avaliable_location'])
        if 'fetter' in character_dict and isinstance(character_dict['fetter'], list):
            character_dict['fetter'] = json.dumps(character_dict['fetter'])
        if 'hate_matrix' in character_dict and isinstance(character_dict['hate_matrix'], list):
            character_dict['hate_matrix'] = json.dumps(character_dict['hate_matrix'])
        
        set_clause = ', '.join([f'{key} = ?' for key in character_dict.keys()])
        query = f'UPDATE character SET {set_clause} WHERE id = ?'
        
        cursor.execute(query, list(character_dict.values()) + [character_id])
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        
        return rowcount
    
    def delete(self, character_id):
        """
        删除一个 character 记录
        :param character_id: character 的 ID
        :return: 删除的行数
        """
        conn = connect_database(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM character WHERE id = ?', (character_id,))
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        
        return rowcount

    # --- character 动态列支持 ---
    def get_character_columns(self):
        """返回 character 表的列名列表"""
        conn = connect_database(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info('character')")
        rows = cursor.fetchall()
        conn.close()
        cols = [row['name'] if isinstance(row, sqlite3.Row) else row[1] for row in rows]
        return cols

    def add_character_column(self, col_id, default_value=None, label=None):
        """
        向 character 表添加新列，并为已有行填充默认值；同时将列元数据写入 character_extra_fields
        :param col_id: 列名（仅允许字母、数字、下划线，且以字母开头）
        :param default_value: 默认值（将以文本形式存储）
        :param label: 中文标签，存入元数据表
        """
        # 简单验证列名
        import re
        if not re.match(r'^[A-Za-z][A-Za-z0-9_]*$', col_id):
            raise ValueError('col_id 必须以字母开头，只能包含字母、数字和下划线')

        conn = connect_database(self.db_path)
        cursor = conn.cursor()

        # 添加列（作为 TEXT）
        sql = f'ALTER TABLE character ADD COLUMN "{col_id}" TEXT'
        try:
            cursor.execute(sql)
        except Exception as e:
            conn.close()
            raise

        # 为已有行填充默认值（如果提供）
        if default_value is not None:
            try:
                cursor.execute(f'UPDATE character SET "{col_id}" = ? WHERE "{col_id}" IS NULL', (str(default_value),))
            except Exception:
                pass

        # 将元数据写入 character_extra_fields
        try:
            cursor.execute('INSERT OR REPLACE INTO character_extra_fields (col_id, label) VALUES (?, ?)', (col_id, label))
        except Exception:
            pass

        conn.commit()
        conn.close()

    def get_character_extra_fields(self):
        """返回 character_extra_fields 表中的所有记录，格式为 [{'col_id':..,'label':..}, ...]"""
        conn = connect_database(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT col_id, label FROM character_extra_fields')
            rows = cursor.fetchall()
        except Exception:
            rows = []
        conn.close()
        out = []
        for r in rows:
            if isinstance(r, sqlite3.Row):
                out.append({'col_id': r['col_id'], 'label': r['label']})
            else:
                out.append({'col_id': r[0], 'label': r[1]})
        return out


class KeywordDao:
    """
    关键词注册表的数据访问对象
    表结构: id TEXT PRIMARY KEY, name TEXT, description TEXT, type TEXT, trigger TEXT, condition TEXT(JSON), effects TEXT(JSON list)
    """
    def __init__(self, db_path=None):
        self.db_path = db_path if db_path else DB_PATH
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        """确保 keyword 表存在"""
        conn = connect_database(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keyword (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                type TEXT,
                trigger TEXT,
                condition TEXT,
                effects TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def create(self, kw_dict):
        conn = connect_database(self.db_path)
        cursor = conn.cursor()
        data = kw_dict.copy()
        # JSON fields
        if 'condition' in data and isinstance(data['condition'], (dict, list)):
            data['condition'] = json.dumps(data['condition'], ensure_ascii=False)
        if 'effects' in data and isinstance(data['effects'], (list, dict)):
            data['effects'] = json.dumps(data['effects'], ensure_ascii=False)

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f'INSERT INTO keyword ({columns}) VALUES ({placeholders})'

        cursor.execute(query, list(data.values()))
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount

    def read(self, kw_id):
        conn = connect_database(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM keyword WHERE id = ?', (kw_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            d = dict(row)
            if d.get('condition'):
                try:
                    d['condition'] = json.loads(d['condition'])
                except:
                    pass
            if d.get('effects'):
                try:
                    d['effects'] = json.loads(d['effects'])
                except:
                    pass
            return d
        return None

    def read_all(self):
        conn = connect_database(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM keyword ORDER BY id')
        rows = cursor.fetchall()
        conn.close()
        out = []
        for row in rows:
            d = dict(row)
            if d.get('condition'):
                try:
                    d['condition'] = json.loads(d['condition'])
                except:
                    pass
            if d.get('effects'):
                try:
                    d['effects'] = json.loads(d['effects'])
                except:
                    pass
            out.append(d)
        return out


class EventDao:
    """事件（event）数据访问对象
    表结构: id(TEXT PK), name(TEXT), context(TEXT as JSON dict)
    """
    def __init__(self, db_path=None):
        self.db_path = db_path if db_path else DB_PATH
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        conn = connect_database(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event (
                id TEXT PRIMARY KEY,
                name TEXT,
                context TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def create(self, event_dict):
        conn = connect_database(self.db_path)
        cursor = conn.cursor()
        data = event_dict.copy()
        if 'context' in data and isinstance(data['context'], (dict, list)):
            data['context'] = json.dumps(data['context'], ensure_ascii=False)

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f'INSERT INTO event ({columns}) VALUES ({placeholders})'
        cursor.execute(query, list(data.values()))
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount

    def read(self, event_id):
        conn = connect_database(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM event WHERE id = ?', (event_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            d = dict(row)
            if d.get('context'):
                try:
                    d['context'] = json.loads(d['context'])
                except:
                    pass
            return d
        return None

    def read_all(self):
        conn = connect_database(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM event ORDER BY id')
        rows = cursor.fetchall()
        conn.close()
        out = []
        for row in rows:
            d = dict(row)
            if d.get('context'):
                try:
                    d['context'] = json.loads(d['context'])
                except:
                    pass
            out.append(d)
        return out

    def update(self, event_id, event_dict):
        conn = connect_database(self.db_path)
        cursor = conn.cursor()
        data = event_dict.copy()
        if 'context' in data and isinstance(data['context'], (dict, list)):
            data['context'] = json.dumps(data['context'], ensure_ascii=False)
        set_clause = ', '.join([f'{k} = ?' for k in data.keys()])
        query = f'UPDATE event SET {set_clause} WHERE id = ?'
        cursor.execute(query, list(data.values()) + [event_id])
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount

    def delete(self, event_id):
        conn = connect_database(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM event WHERE id = ?', (event_id,))
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount

    def init_from_doc(self, doc_path=None):
        """从文档规范/事件文档.md 读取基础事件并写入表（不会删除已有不同 id 的记录）"""
        if doc_path is None:
            doc_path = BASE_DIR.parent / '文档规范' / '事件文档.md'
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                lines = [ln.rstrip() for ln in f]
        except Exception:
            return False

        events = []
        current = None
        for ln in lines:
            ln = ln.strip()
            if not ln:
                continue
            # top-level event line starting with on...
            if ln.startswith('on'):
                # split by -> if present
                parts = ln.split('->')
                left = parts[0].strip()
                desc = parts[1].strip() if len(parts) > 1 else ''
                # left may be like onAttack(source: Character, target: Character)
                sig = left
                eid = sig.split('(')[0]
                name = desc or eid
                current = {'id': eid, 'name': name, 'context': {'signature': sig, 'description': desc, 'subevents': []}}
                events.append(current)
            elif ln.startswith('-') and current is not None:
                sub = ln.lstrip('-').strip()
                current['context']['subevents'].append(sub)

        # insert events if not exists
        conn = connect_database(self.db_path)
        cursor = conn.cursor()
        for ev in events:
            try:
                cursor.execute('SELECT id FROM event WHERE id = ?', (ev['id'],))
                if cursor.fetchone():
                    continue
                cursor.execute('INSERT INTO event (id, name, context) VALUES (?, ?, ?)', (ev['id'], ev['name'], json.dumps(ev['context'], ensure_ascii=False)))
            except Exception:
                pass
        conn.commit()
        conn.close()
        return True

    def update(self, kw_id, kw_dict):
        conn = connect_database(self.db_path)
        cursor = conn.cursor()
        data = kw_dict.copy()
        if 'condition' in data and isinstance(data['condition'], (dict, list)):
            data['condition'] = json.dumps(data['condition'], ensure_ascii=False)
        if 'effects' in data and isinstance(data['effects'], (list, dict)):
            data['effects'] = json.dumps(data['effects'], ensure_ascii=False)

        set_clause = ', '.join([f'{k} = ?' for k in data.keys()])
        query = f'UPDATE keyword SET {set_clause} WHERE id = ?'
        cursor.execute(query, list(data.values()) + [kw_id])
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount

    def delete(self, kw_id):
        conn = connect_database(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM keyword WHERE id = ?', (kw_id,))
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount



def dumpJson(output_path=None, db_path=None):
    """
    将 character 表导出为 JSON 文件
    :param output_path: 输出 JSON 文件路径，默认为 character_export.json
    :param db_path: 数据库文件路径
    :return: 导出是否成功
    """
    if output_path is None:
        output_path = BASE_DIR.parent / "py灰盒" / "character_config.json"
    
    dao = CharacterDao(db_path)
    characters = dao.read_all()
    
    # 转换为以 id 为键的字典格式
    character_dict = {}
    for char in characters:
        char_id = char.pop('id')
        # 将 id 重新加入到字典中
        char['id'] = char_id
        character_dict[char_id] = char
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(character_dict, f, ensure_ascii=False, indent=2)
    
    return True


def updateDb(db_path=None):
    """
    清空 database.db 并根据 sql 文件夹内的 .sql 文件重构整个数据库
    :param db_path: 数据库文件路径
    :return: 是否成功
    """
    if db_path is None:
        db_path = DB_PATH
    
    # 如果数据库文件存在，删除它
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # 创建新的数据库连接
    conn = connect_database(db_path)
    cursor = conn.cursor()
    
    # 查找所有 .sql 文件并执行
    sql_files = sorted(SQL_DIR.glob('*.sql'))
    
    if not sql_files:
        # 如果没有 SQL 文件，创建默认表结构
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS character (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                localization TEXT,
                attack_power INTEGER DEFAULT 4,
                health_points INTEGER DEFAULT 8,
                speed INTEGER DEFAULT 2,
                hate_value INTEGER DEFAULT 1,
                price INTEGER DEFAULT 1,
                weapon TEXT,
                energy INTEGER DEFAULT 0,
                avaliable_location TEXT,
                fetter TEXT,
                hate_matrix TEXT
            )
        ''')
        # 关键字注册表，用于可视化管理常用关键词
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keyword (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                type TEXT,
                trigger TEXT,
                condition TEXT,
                effects TEXT
            )
        ''')
        # character 额外字段元数据表：记录动态添加到 character 表中的列及其中文标签
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS character_extra_fields (
                col_id TEXT PRIMARY KEY,
                label TEXT
            )
        ''')
    else:
        for sql_file in sql_files:
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_script = f.read()
                cursor.executescript(sql_script)
    
    conn.commit()
    conn.close()
    
    return True


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
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    conn = connect_database(db_path)
    
    # 导出数据库结构和数据
    with open(output_dir / 'database_dump.sql', 'w', encoding='utf-8') as f:
        for line in conn.iterdump():
            f.write(f'{line}\n')
    
    conn.close()
    
    return True


if __name__ == '__main__':
    # 测试代码
    dao = CharacterDao()
    
    # 测试创建
    test_char = {
        'id': '9999',
        'name': 'test_character',
        'attack_power': 10,
        'health_points': 100,
        'speed': 5
    }
    dao.create(test_char)
    
    # 测试读取
    char = dao.read('9999')
    print('Read:', char)
    
    # 测试更新
    dao.update('9999', {'attack_power': 15})
    char = dao.read('9999')
    print('After update:', char)
    
    # 测试删除
    dao.delete('9999')
    char = dao.read('9999')
    print('After delete:', char)
