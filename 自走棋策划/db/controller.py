import sys, os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import service as service

class CharacterControl:
    def __init__(self):
        self.char_service : service.CharacterService = service.CharacterService()

    def get_all_characters(self):
        """
        获取所有角色信息
        """
        try:
            res = self.char_service.select_all_characters()
            return res
        except Exception as e:
            print("Error getting all characters:", e)
            return []

    def get_character_by_id(self, char_id):
        """
        根据ID获取角色信息
        """
        try:
            res = self.char_service.select_character_by_id(int(char_id))
            return res
        except Exception as e:
            print("Error getting character by ID:", e)
            return {}

    def get_characters_by_price(self, price):
        """
        根据价格获取角色信息
        """
        try:
            res = self.char_service.select_character_by_price(price)
            return res
        except Exception as e:
            print("Error getting characters by price:", e)
            return []

    def add_character(self, character: dict):
        """
        添加新角色
        """
        try:
            self.char_service.insert_character(character)
            return True
        except Exception as e:
            print("Error adding character:", e)
            return False

    def add_character_column(self, column_info: dict):
        """
        向角色表中添加新列
        """
        try:
            self.char_service.insert_column(column_info)
            return True
        except Exception as e:
            print("Error adding character column:", e)
            return False
        
    def get_next_character_id(self):
        """
        获取下一个可用的角色ID
        """
        try:
            next_id = self.char_service.get_next_character_id()
            return next_id
        except Exception as e:
            print("Error getting next character ID:", e)
            return None
    
    def get_all_columns(self):
        """
        获取角色表的所有列名
        """
        try:
            columns = self.char_service.get_all_columns()
            return columns
        except Exception as e:
            print("Error getting all columns:", e)
            return []
        
    def update_character(self, char_id: int, updates: dict):
        """
        
        """
        try:
            res = self.char_service.update_character(char_id, updates)
            return res
        except Exception as e:
            print("Error update character:", e)
            return False
        
    def delete_character(self, char_id: int):
        """
        删除角色
        """
        try:
            res = self.char_service.delete_character(char_id)
            return res
        except Exception as e:
            print("Error delete character:", e)
            return False
        
    def dumpJson(self):
        """
        导出 JSON 文件
        """
        try:
            service.dumpJson()
        except Exception as e:
            print("Error dumping JSON:", e)

class FetterControl:
    def __init__(self):
        self.fetter_service : service.FetterService = service.FetterService()

    def get_all_fetters(self):
        """
        获取所有羁绊信息
        """
        try:
            res = self.fetter_service.get_all_fetters()
            return res
        except Exception as e:
            print("Error getting all fetters:", e)
            return []
    
    def get_fetter_by_id(self, fetter_id):
        """
        根据羁绊ID获取羁绊信息
        """
        try:
            res = self.fetter_service.get_fetter_by_id(int(fetter_id))
            return res
        except Exception as e:
            print("Error getting fetter by ID:", e)
            return {}

    def insert_fetter(self, fetter: dict):
        """
        插入新羁绊
        """
        try:
            self.fetter_service.insert_fetter(fetter)
            return True
        except Exception as e:
            print("Error inserting fetter:", e)
            return False

    def update_fetter(self, fetter_key: tuple, updates: dict):
        """
        更新羁绊信息
        """
        try:
            res = self.fetter_service.update_fetter(fetter_key, updates)
            return res
        except Exception as e:
            print("Error updating fetter:", e)
            return False

    def delete_fetter(self, fetter_key: tuple):
        """
        删除羁绊
        """
        try:
            res = self.fetter_service.delete_fetter(fetter_key)
            return res
        except Exception as e:
            print("Error deleting fetter:", e)
            return False

    def dumpJson(self):
        """
        导出 JSON 文件
        """
        try:
            self.fetter_service.dumpJson()
        except Exception as e:
            print("Error dumping JSON:", e)
            return False

if __name__ == "__main__":
    pass