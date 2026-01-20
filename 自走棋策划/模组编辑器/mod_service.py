import mod_dao as dao
from mod_dao import t

class ModService:
    def __init__(self, modid):
        self.modid = modid
        self.dao = dao.ModDao(modid)

    def init_directory(self):
        res = self.dao.init_mod_directory()
        if res:
            char = dao.get_default_character()
            CharacterService(self.modid).create_character(char)
        return res

class CharacterService:
    def __init__(self, modid):
        self.modid = modid
        self.dao = dao.CharacterDao(modid)

    def get_all_character(self):
        char_ids = self.dao.get_all_character_ids()
        characters = []
        for cid in char_ids:
            character = self.dao.get_character_by_id(cid)
            if character:
                characters.append(character)
        return characters

    def get_character_by_id(self, char_id):
        char_data = self.dao.get_character_by_id(char_id)
        for key, value in char_data.items():
            if isinstance(value, str):
                if '.' in value:
                    char_data[key] = t(self.modid, dao.get_default_language(self.modid), value)
        return char_data

    def create_character(self, char_data):
        char = dao.get_default_character()
        new_keys = []
        for key in char:
            if key in ['name', 'background', 'description']:
                lang_key = f"{self.modid}.character.{char_data.get('id')}.{key}"
                char[key] = lang_key
                new_keys.append(lang_key)
            else:
                if key in char_data:
                    char[key] = char_data[key]
        res = self.dao.create_character(char)
        if res:
            for lang_key in new_keys:
                key = lang_key.split('.')[-1]
                dao.LangDao.set_lang(self.dao.modid, lang_key, char_data.get(key, ''))
            dao.LangDao.add_lang_key(self.dao.modid, new_keys)
        return res

    def update_character(self, char_id, char_data):
        for key in ['name', 'background', 'description']:
            lang_key = f"{self.modid}.character.{char_id}.{key}"
            dao.LangDao.set_lang(self.dao.modid, lang_key, char_data.get(key, ''))
        return self.dao.update_character(char_id, char_data)

    def delete_character(self, char_id):
        lang_keys = [
            f"{self.modid}.character.{char_id}.{key}"
            for key in ['name', 'background', 'description']
        ]
        res = self.dao.delete_character(char_id)
        if res:
            dao.LangDao.del_lang(self.dao.modid, lang_keys)
            dao.LangDao.remove_lang_key(self.dao.modid, lang_keys)
        return res

    def get_characters_by_price(self, price):
        all_chars = self.get_all_character()
        filtered_chars = [char for char in all_chars if char.get('price') == price]
        return filtered_chars
    
    def get_default_fields(self):
        default_char = self.dao.get_default_character()
        if default_char:
            return list(default_char.keys())
        return []