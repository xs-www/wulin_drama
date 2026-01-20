
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