
from uuid6 import uuid7
import json, sys, os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dao as dao
class CharacterService:
    def __init__(self):
        self.char_dao : dao.CharacterDao = dao.CharacterDao()
        self.char_fetter_dao : dao.CharacterFetterDao = dao.CharacterFetterDao()

    def select_all_characters(self):
        """
        获取所有角色信息
        :return: 角色信息列表
        """
        conn = dao.connect_database()
        res = self.char_dao.select_all_characters(conn)
        for char in res:
            for k, v in char.items():
                if k in ['weapon', 'avaliable_location', 'hate_matrix']:
                    if v:
                        char[k] = json.loads(v.replace("'", ''))
                    else:
                        char[k] = []
            char["fetters"] = self.char_fetter_dao.get_fetters_by_char_id(char.get("id"), conn)
        conn.close()
        return res

    def select_character_by_id(self, char_id):
        """
        根据角色ID获取角色信息
        :param char_id: 角色ID
        :return: 角色信息字典
        """
        conn = dao.connect_database()
        res = self.char_dao.select_character_by_id(char_id, conn)
        for k, v in res.items():
            if k in ['weapon', 'avaliable_location', 'hate_matrix']:
                if v:
                    res[k] = json.loads(v.replace("'", ''))
                else:
                    res[k] = []
        res["fetters"] = self.char_fetter_dao.get_fetters_by_char_id(res.get("id"), conn)
        conn.close()
        return res

    def select_character_by_price(self, price):
        """
        根据价格获取角色信息
        :param price: 角色价格
        :return: 角色信息列表
        """
        conn = dao.connect_database()
        res = self.char_dao.select_character_by_price(price, conn)
        for char in res:
            for k, v in char.items():
                if k in ['weapon', 'avaliable_location', 'hate_matrix']:
                    if v:
                        char[k] = json.loads(v.replace("'", ''))
                    else:
                        char[k] = []
            char["fetters"] = self.char_fetter_dao.get_fetters_by_char_id(char.get("id"), conn)
        conn.close()
        return res

    def insert_character(self, character: dict):
        """
        插入新角色
        :param character: 角色信息字典
        """
        print(character)
        conn = dao.connect_database()
        character.pop('id')
        values = [None]
        for field in list(self.char_dao.mapper.get("fields").keys())[1:]:
            if field == "localization" and character.get("localization", None) is None:
                default_value = character.get("name")
            else:
                default_value = self.char_dao.mapper.get("fields").get(field).get("default", None)
            value = character.get(field, default_value)
            values.append(value)
        cid = self.char_dao.insert_character(values, conn)

        # 处理羁绊关联
        fetters_name = character.get("fetters", [])
        fdao = dao.FetterDao()
        for fetter_name in fetters_name:
            fetter_info = fdao.select_fetter_by_id(fetter_name, conn)
            if fetter_info is None:
                raise ValueError(f"Fetter '{fetter_name}' does not exist")
            fetter_id = fetter_info[0].get("id")
            char_fetter_values = [cid, fetter_id]
            self.char_fetter_dao.insert_character_fetter(char_fetter_values, conn)

        conn.commit()
        conn.close()
        return

    def update_character(self, char_id, updates: dict):
        """
        更新角色信息
        :param char_id: 角色ID
        :param updates: 更新内容字典
        """
        conn = dao.connect_database()
        values = []
        for field in list(self.char_dao.mapper.get("fields").keys())[1:]:
            default_value = self.char_dao.mapper.get("fields").get(field).get("default", None)
            value = updates.get(field, default_value)
            if isinstance(value, (list, dict)):
                value = json.dumps(value, ensure_ascii=False)
            values.append(value)
        self.char_dao.update_character(char_id, values, conn)

        # 处理羁绊关联
        fetters_name = json.loads(updates.get("fetters", "[]").replace("\'", "\""))
        print(fetters_name)
        fdao = dao.FetterDao()
        self.char_fetter_dao.delete_character_fetter_by_char_id(char_id, conn)
        for fetter_name in fetters_name:
            fetter_info = fdao.select_fetter_by_id(fetter_name, conn)
            if fetter_info is None:
                raise ValueError(f"Fetter '{fetter_name}' does not exist")
            fetter_id = fetter_info[0].get("id")
            char_fetter_values = [char_id, fetter_id]
            self.char_fetter_dao.insert_character_fetter(char_fetter_values, conn)
        conn.commit()
        conn.close()
        return True

    def insert_column(self, column: dict):
        """
        向角色表中添加新列
        :param name: 列名
        :param type: 列类型
        :param default: 默认值
        """
        conn = dao.connect_database()
        column_name = column.get("name", None)
        column_type = column.get("type", None)
        if column_name is None or column_type is None:
            raise ValueError("Column name and type are required")
        default_value = column.get("default", None)
        not_null = column.get("not_null", False)
        column_info = {
            "type": column_type,
            "default": default_value
        }
        if not_null:
            column_info["not_null"] = True
        self.char_dao.insert_column_to_mapper(column_name, column_info)
        dao.update_mapper("Character")
        self.char_dao.insert_column(column_name, column_type, default_value, not_null, conn)

        conn.commit()
        conn.close()


    def delete_character(self, char_id):
        """
        删除角色
        :param char_id: 角色ID
        """
        conn = dao.connect_database()
        self.char_dao.delete_character(char_id, conn)

        conn.commit()
        conn.close()

    def delete_column(self, column_name):
        """
        删除角色表中的列
        :param column_name: 列名
        """
        conn = dao.connect_database()
        characters = self.char_dao.select_all_characters(conn)
        dao.drop_table("Character")
        dao.drop_table("CharacterFetter")
        for char in characters:
            char.pop(column_name, None)
        self.char_dao.delete_column_from_mapper(column_name)
        dao.create_table("Character")
        dao.create_table("CharacterFetter")
        for char in characters:
            self.insert_character(char, conn)
        conn.commit()
        conn.close()

    def get_next_character_id(self):
        """
        获取下一个可用的角色ID
        :return: 下一个角色ID
        """
        conn = dao.connect_database()
        res = self.char_dao.get_next_id(conn)
        conn.close()
        return res if res else 1
    
    def get_all_columns(self):
        """"""
        res = list(self.char_dao.mapper.get("fields").keys())
        res.append("fetters")
        return res

    def dumpJson(self):
        """
        导出 JSON 文件
        """
        import os
        characters = self.select_all_characters()
        path = "data/characters/"
        with open(os.path.join(path, "characters.json"), "w", encoding="utf-8") as f:
            json.dump(characters, f, ensure_ascii=False, indent=4)


class FetterService:
    def __init__(self):
        self.fetter_dao = dao.FetterDao()

    def get_all_fetters(self):
        """
        获取所有羁绊信息
        :return: 羁绊信息列表
        """
        conn = dao.connect_database()
        res = self.fetter_dao.select_all_fetters(conn)
        conn.close()
        return res

    def get_fetter_by_id(self, fetter_id):
        """
        根据羁绊ID获取羁绊信息
        :param fetter_id: 羁绊ID
        :return: 羁绊信息字典
        """
        conn = dao.connect_database()
        res = self.fetter_dao.select_fetter_by_id(fetter_id, conn)
        conn.close()
        return res
    
    def insert_fetter(self, fetter: dict):
        """
        插入新羁绊
        :param fetter: 羁绊信息字典
        """
        """
        fetter = {
            "id": n,
            "numofpeople": y,
            "localization": "name",
            "description": "text"
        }
        """
        conn = dao.connect_database()
        values = []
        for field in self.fetter_dao.mapper.get("fields").keys():
            default_value = self.fetter_dao.mapper.get("fields").get(field).get("default", None)
            value = fetter.get(field, default_value)
            values.append(value)
        self.fetter_dao.insert_fetter(values, conn)

        conn.commit()
        conn.close()
        return

    def update_fetter(self, fetter_key: tuple, updates: dict):
        """
        更新羁绊信息
        :param fetter_id: 羁绊ID
        :param updates: 更新内容字典
        """
        conn = dao.connect_database()
        updates_list = list(updates.values())
        self.fetter_dao.update_fetter(fetter_key, updates_list, conn)
        conn.commit()
        conn.close()
        return True

    def delete_fetter(self, fetter_key: tuple):
        """
        删除羁绊
        :param fetter_key: 羁绊唯一标识 (ID, numofpeople)
        """
        conn = dao.connect_database()
        self.fetter_dao.delete_fetter(*fetter_key, conn)
        conn.commit()
        conn.close()
        return True

    def dumpJson(self):
        """
        导出 JSON 文件
        """
        import os
        fetters = self.get_all_fetters()
        path = "data/fetters/"
        with open(os.path.join(path, "fetters.json"), "w", encoding="utf-8") as f:
            json.dump(fetters, f, ensure_ascii=False, indent=4)
    

if __name__ == "__main__":
    cserv = CharacterService()
    conn = dao.connect_database()

    fdao = dao.FetterDao()
    cfdao = dao.CharacterFetterDao()

    try:
        print(cserv.select_character_by_id(1))
    except Exception as e:
        print("Error", e)

    conn.commit()
    conn.close()