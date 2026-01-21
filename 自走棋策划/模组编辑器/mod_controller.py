
import mod_service as service

class ModController:
    def __init__(self, modid):
        self.modid = modid
        self.service = service.ModService(modid)

    def get_mod_path(self):
        return self.service.dao.mod_path

    def init_mod_directory(self):
        try:
            self.service.init_directory()
            return True
        except Exception as e:
            print(f"Error initializing mod directory: {e}")
            return False

    def export_mod(self, export_path=None):
        try:
            return self.service.export_mod(export_path)
        except Exception as e:
            print(f"Error exporting mod: {e}")
            return False

class CharacterController:
    def __init__(self, modid):
        self.service = service.CharacterService(modid)

    def get_all_characters(self):
        try:
            res = self.service.get_all_character()
        except Exception as e:
            print(f"Error listing characters: {e}")
            res = []
        return res

    def get_character_by_id(self, char_id):
        try:
            return self.service.get_character_by_id(char_id)
        except Exception as e:
            print(f"Error getting character {char_id}: {e}")
            return None
        
    def get_default_fields(self):
        try:
            res = self.service.get_default_fields()
        except Exception as e:
            print(f"Error getting default fields: {e}")
            res = []
        return res

    def create_character(self, char_data):
        try:
            return self.service.create_character(char_data)
        except Exception as e:
            print(f"Error creating character: {e}")
            return False

    def update_character(self, char_id, char_data):
        try:
            return self.service.update_character(char_id, char_data)
        except Exception as e:
            print(f"Error updating character {char_id}: {e}")
            return False

    def delete_character(self, char_id):
        try:
            return self.service.delete_character(char_id)
        except Exception as e:
            print(f"Error deleting character {char_id}: {e}")
            return False
        
class FetterController:
    def __init__(self, modid):
        self.service = service.FetterService(modid)

    def get_all_fetters(self):
        try:
            res = self.service.get_all_fetters()
        except Exception as e:
            print(f"获取羁绊列表失败: {e}")
            res = []
        return res

    def get_fetter_by_id(self, fetter_id):
        try:
            return self.service.get_fetter_by_id(fetter_id)
        except Exception as e:
            print(f"获取羁绊 {fetter_id} 失败: {e}")
            return None

    def save_fetter(self, fetter_dict):
        try:
            res = self.service.save_fetter(fetter_dict)
        except Exception as e:
            print(f"保存羁绊失败: {e}")
            res = False
        return res

    def create_fetter(self, fetter_data):
        try:
            return self.service.create_fetter(fetter_data)
        except Exception as e:
            print(f"创建羁绊失败: {e}")
            return False
    
    def update_fetter(self, fetter_id, fetter_data):
        try:
            return self.service.update_fetter(fetter_id, fetter_data)
        except Exception as e:
            print(f"更新羁绊 {fetter_id} 失败: {e}")
            return False
    
    def delete_fetter(self, fetter_id):
        try:
            return self.service.delete_fetter(fetter_id)
        except Exception as e:
            print(f"删除羁绊 {fetter_id} 失败: {e}")
            return False
    
    def gen_description(self, effects_dict):
        try:
            return self.service.gen_description(effects_dict)
        except Exception as e:
            print(f"生成羁绊描述失败: {e}")
            return f"生成羁绊描述失败: {e}"
    
