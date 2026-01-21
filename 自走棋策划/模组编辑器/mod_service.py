import mod_dao as dao
from mod_dao import t
from utils import effect_parser
import re

class ModService:
    def __init__(self, modid):
        self.modid = modid
        self.dao = dao.ModDao(modid)

    def init_directory(self):
        res = self.dao.init_mod_directory()
        if res:
            char = dao.get_default_data('character')
            CharacterService(self.modid).create_character(char)
            fet = dao.get_default_data('faction')
            FactionService(self.modid).create_faction(fet)

        return res
    
    def export_mod(self, export_path=None):
        return self.dao.export_mod(export_path)

class CharacterService:
    def __init__(self, modid):
        self.modid = modid
        self.dao = dao.CharacterDao(modid)

    def get_all_character(self):
        char_ids = self.dao.get_all_character_ids()
        characters = []
        for cid in char_ids:
            character = self.get_character_by_id(cid)
            if character:
                characters.append(character)
        return characters

    def get_character_by_id(self, char_id):
        if char_id.startswith(f"{self.modid}:character/"):
            char_id = char_id.split('/')[-1]
        char_data = self.dao.get_character_by_id(char_id)
        for key, value in char_data.items():
            if isinstance(value, str):
                if '.' in value:
                    char_data[key] = t(self.modid, dao.get_default_language(self.modid), value)
        return char_data

    def create_character(self, char_data):
        char = dao.get_default_data('character')
        new_keys = []
        for key in char:
            if key in ['name', 'background', 'description']:
                lang_key = f"{self.modid}.character.{char_data.get('id')}.{key}"
                char[key] = lang_key
                new_keys.append(lang_key)
            else:
                if key in char_data:
                    char[key] = char_data[key]
        char['id'] = f"{self.modid}:character/{char_data.get('id')}"
        res = self.dao.create_character(char_data.get('id'), char)
        if res:
            for lang_key in new_keys:
                key = lang_key.split('.')[-1]
                dao.LangDao.set_lang(self.modid, lang_key, char_data.get(key, ''))
            dao.LangDao.add_lang_key(self.modid, new_keys)
        return res

    def update_character(self, char_data):
        char_id = char_data.get('id')
        if char_id.startswith(f"{self.modid}:character/"):
            char_id = char_id.split('/')[-1]
        for key in ['name', 'background', 'description']:
            lang_key = f"{self.modid}.character.{char_id}.{key}"
            dao.LangDao.set_lang(self.modid, lang_key, char_data.get(key, ''))
        return self.dao.update_character(char_id, char_data)

    def delete_character(self, char_id):
        lang_keys = [
            f"{self.modid}.character.{char_id}.{key}"
            for key in ['name', 'background', 'description']
        ]
        res = self.dao.delete_character(char_id)
        if res:
            dao.LangDao.del_lang(self.modid, lang_keys)
            dao.LangDao.remove_lang_key(self.modid, lang_keys)
        return res

    def get_characters_by_price(self, price):
        all_chars = self.get_all_character()
        filtered_chars = [char for char in all_chars if char.get('price') == price]
        return filtered_chars
    
    def get_default_fields(self):
        default_char = dao.get_default_data('character')
        if default_char:
            return list(default_char.keys())
        return []
    
class FactionService:
    def __init__(self, modid):
        self.modid = modid
        self.dao = dao.FactionDao(modid)

    def get_all_factions(self) -> list[dict]:
        faction_ids = self.dao.get_all_faction_ids()
        factions = []
        for fid in faction_ids:
            faction = self.get_faction_by_id(fid)
            if faction:
                factions.append(faction)
        return factions
    
    def get_faction_by_id(self, faction_id):
        if faction_id.startswith(f"{self.modid}:faction/"):
            faction_id = faction_id.split('/')[-1]
        faction_data = self.dao.get_faction_by_id(faction_id)
        for key, value in faction_data.items():
            if isinstance(value, str):
                if '.' in value:
                    faction_data[key] = t(self.modid, dao.get_default_language(self.modid), value)
        return faction_data

    def create_faction(self, faction_data):
        faction = dao.get_default_data('faction')
        faction['effects'] = {}
        new_keys = []
        for key in faction:
            if key in ['name', 'description']:
                lang_key = f"{self.modid}.faction.{faction_data.get('id')}.{key}"
                faction[key] = lang_key
                new_keys.append(lang_key)
            else:
                if key in faction_data:
                    faction[key] = faction_data[key]
        faction_id = f"{self.modid}:faction/{faction_data.get('id')}"
        faction['id'] = faction_id
        res = self.dao.create_faction(faction_data.get('id'), faction)
        if res:
            for lang_key in new_keys:
                key = lang_key.split('.')[-1]
                dao.LangDao.set_lang(self.modid, lang_key, faction_data.get(key, ''))
            dao.LangDao.add_lang_key(self.modid, new_keys)
        return res

    def update_faction(self, faction_data):
        faction_id = faction_data.get('id')
        if faction_id.startswith(f"{self.modid}:faction/"):
            faction_id = faction_id.split('/')[-1]
        res = self.dao.update_faction(faction_id, faction_data)
        if res:
            for key in ['name', 'description']:
                lang_key = f"{self.modid}.faction.{faction_id}.{key}"
                dao.LangDao.set_lang(self.modid, lang_key, faction_data.get(key, ''))
                faction_data[key] = lang_key

    def save_faction(self, faction_dict):
        faction_id = faction_dict.get('id')
        if self.dao.has_id(faction_id):
            return self.update_faction(faction_id, faction_dict)
        else:
            return self.create_faction(faction_dict)

    def delete_faction(self, faction_id):
        lang_keys = [
            f"{self.modid}.faction.{faction_id}.{key}"
            for key in ['name', 'description']
        ]
        res = self.dao.delete_faction(faction_id)
        if res:
            dao.LangDao.del_lang(self.modid, lang_keys)
            dao.LangDao.remove_lang_key(self.modid, lang_keys)
        return res
    
    def gen_description(self, effects_dict: dict):

        def extract_simple(s):
            # 非贪婪匹配，返回不含括号的内容列表
            return re.findall(r'\((.*?)\)', s)

        def convert_brackets_into_QM(s):
            # 将括号同里面的内容替换为问号
            return re.sub(r'\(.*?\)', '?', s)

        nums = []
        res = ''
        for effs in effects_dict.values():
            word = ''
            for eff in effs:
                word += effect_parser(eff, highlight_num=True) + ','
            if not nums:
                nums = extract_simple(word)
            else:
                for i in range(len(extract_simple(word))):
                    if extract_simple(word)[i] not in nums:
                        nums[i] += f"/{extract_simple(word)[i]}"
            if not res:
                res = convert_brackets_into_QM(word)
            else:
                if res != convert_brackets_into_QM(word):
                    raise ValueError("不同效果描述的格式不一致，无法生成统一描述")
        
        res = res.split('?')
        keys = '/'.join(list(effects_dict.keys()))
        for w in range(len(res)-1):
            res[w] += f" {nums[w]} "
        res = ''.join(res)
        res = f"当人数达到 {keys} 时激活：{res}"[:-1] + '。'
        return res

if __name__ == "__main__":
    modid = 'test'
    fs = FactionService(modid)
    aaa = fs.get_faction_by_id('aaa')
    print(fs.gen_description(aaa.get('effects', {})))