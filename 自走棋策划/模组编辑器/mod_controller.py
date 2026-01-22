
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
        self.modid = modid
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
            return self.service.create_character(char_data.copy())
        except Exception as e:
            print(f"Error creating character: {e}")
            return False

    def update_character(self, char_data):
        try:
            return self.service.update_character(char_data.copy())
        except Exception as e:
            print(f"Error updating character: {e}")
            return False

    def delete_character(self, char_id):
        try:
            return self.service.delete_character(char_id)
        except Exception as e:
            print(f"Error deleting character {char_id}: {e}")
            return False
        
class FactionController:
    def __init__(self, modid):
        self.modid = modid
        self.service = service.FactionService(modid)

    def get_all_factions(self):
        try:
            res = self.service.get_all_factions()
        except Exception as e:
            print(f"获取羁绊列表失败: {e}")
            res = []
        return res

    def get_faction_by_id(self, faction_id):
        try:
            return self.service.get_faction_by_id(faction_id)
        except Exception as e:
            print(f"获取羁绊 {faction_id} 失败: {e}")
            return None

    def save_faction(self, faction_dict):
        try:
            res = self.service.save_faction(faction_dict.copy())
        except Exception as e:
            print(f"保存羁绊失败: {e}")
            res = False
        return res

    def create_faction(self, faction_data):
        try:
            return self.service.create_faction(faction_data)
        except Exception as e:
            print(f"创建羁绊失败: {e}")
            return False
    
    def update_faction(self, faction_data):
        try:
            return self.service.update_faction(faction_data)
        except Exception as e:
            print(f"更新羁绊 {faction_data.get('id')} 失败: {e}")
            return False
    
    def delete_faction(self, faction_id):
        try:
            return self.service.delete_faction(faction_id)
        except Exception as e:
            print(f"删除羁绊 {faction_id} 失败: {e}")
            return False
    
    def gen_description(self, effects_dict) -> dict:
        try:
            return self.service.gen_description(effects_dict)
        except Exception as e:
            print(f"生成羁绊描述失败: {e}")
            return f"生成羁绊描述失败: {e}"
        
class SkillController:
    def __init__(self, modid):
        self.modid = modid
        self.service = service.SkillService(modid)

    def get_all_skills(self):
        try:
            res = self.service.get_all_skills()
        except Exception as e:
            print(f"Error listing skills: {e}")
            res = []
        return res

    def get_skill_by_id(self, skill_id):
        try:
            return self.service.get_skill_by_id(skill_id)
        except Exception as e:
            print(f"Error getting skill {skill_id}: {e}")
            return None

    def create_skill(self, skill_data):
        try:
            return self.service.create_skill(skill_data.copy())
        except Exception as e:
            print(f"Error creating skill: {e}")
            return False

    def update_skill(self, skill_data):
        try:
            return self.service.update_skill(skill_data.copy())
        except Exception as e:
            print(f"Error updating skill: {e}")
            return False

    def delete_skill(self, skill_id):
        try:
            return self.service.delete_skill(skill_id)
        except Exception as e:
            print(f"Error deleting skill {skill_id}: {e}")
            return False

class EventController:
    def __init__(self, modid):
        self.modid = modid
        self.service = service.EventService(modid)

    def get_all_events(self):
        try:
            res = self.service.get_all_events()
        except Exception as e:
            print(f"Error listing events: {e}")
            res = []
        return res

    def get_event_by_id(self, event_id):
        try:
            return self.service.get_event_by_id(event_id)
        except Exception as e:
            print(f"Error getting event {event_id}: {e}")
            return None

    def create_event(self, event_data):
        try:
            return self.service.create_event(event_data.copy())
        except Exception as e:
            print(f"Error creating event: {e}")
            return False

    def update_event(self, event_data):
        try:
            return self.service.update_event(event_data.copy())
        except Exception as e:
            print(f"Error updating event: {e}")
            return False

    def delete_event(self, event_id):
        try:
            return self.service.delete_event(event_id)
        except Exception as e:
            print(f"Error deleting event {event_id}: {e}")
            return False
        
class BuffController:
    def __init__(self, modid):
        self.modid = modid
        self.service = service.BuffService(modid)

    def get_all_buffs(self):
        try:
            res = self.service.get_all_buffs()
        except Exception as e:
            print(f"Error listing buffs: {e}")
            res = []
        return res

    def get_buff_by_id(self, buff_id):
        try:
            return self.service.get_buff_by_id(buff_id)
        except Exception as e:
            print(f"Error getting buff {buff_id}: {e}")
            return None

    def create_buff(self, buff_data):
        try:
            return self.service.create_buff(buff_data.copy())
        except Exception as e:
            print(f"Error creating buff: {e}")
            return False

    def update_buff(self, buff_data):
        try:
            return self.service.update_buff(buff_data.copy())
        except Exception as e:
            print(f"Error updating buff: {e}")
            return False

    def delete_buff(self, buff_id):
        try:
            return self.service.delete_buff(buff_id)
        except Exception as e:
            print(f"Error deleting buff {buff_id}: {e}")
            return False