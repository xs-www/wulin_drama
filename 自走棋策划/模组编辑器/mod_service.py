import mod_dao as dao
from mod_dao import t
from utils import effect_parser
import re, shutil
from pathlib import Path

class ModService:
    def __init__(self, modid):
        self.modid = modid
        self.dao = dao.ModDao(modid)

    def init_directory(self):
        res = self.dao.init_mod_directory()
        BASE_PATH = Path(__file__).resolve().parent
        src = BASE_PATH / 'data' / 'WuLinXi'
        dst = self.dao.mod_path() / 'data' / 'WuLinXi'
        shutil.copytree(src, dst, dirs_exist_ok=True)

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
        return res

    def save_faction(self, faction_dict):
        faction_id = faction_dict.get('id')
        if faction_id.startswith(f"{self.modid}:faction/"):
            faction_id = faction_id.split('/')[-1]
        if self.dao.has_id(faction_id):
            return self.update_faction(faction_dict)
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

class SkillService:
    def __init__(self, modid):
        self.modid = modid
        self.dao = dao.SkillDao(modid)

    def get_all_skills(self) -> list[dict]:
        skill_ids = self.dao.get_all_skill_ids()
        skills = []
        for sid in skill_ids:
            skill = self.get_skill_by_id(sid)
            if skill:
                skills.append(skill)
        return skills
    
    def get_skill_by_id(self, skill_id):
        if skill_id.startswith(f"{self.modid}:skill/"):
            skill_id = skill_id.split('/')[-1]
        skill_data = self.dao.get_skill_by_id(skill_id)
        for key, value in skill_data.items():
            if isinstance(value, str):
                if '.' in value:
                    skill_data[key] = t(self.modid, dao.get_default_language(self.modid), value)
        return skill_data

    def create_skill(self, skill_data):
        skill_id = skill_data.get('id')
        if skill_id.startswith(f"{self.modid}:skill/"):
            skill_id = skill_id.split('/')[-1]
        else:
            skill_data['id'] = f"{self.modid}:skill/{skill_id}"
        res = self.dao.create_skill(skill_id, skill_data)
        if res:
            new_keys = []
            for key in ['name', 'description']:
                lang_key = f"{self.modid}.skill.{skill_id}.{key}"
                skill_data[key] = lang_key
                new_keys.append(lang_key)
            for lang_key in new_keys:
                key = lang_key.split('.')[-1]
                dao.LangDao.set_lang(self.modid, lang_key, skill_data.get(key, ''))
            dao.LangDao.add_lang_key(self.modid, new_keys)
        return res

    def update_skill(self, skill_data):
        skill_id = skill_data.get('id')
        if skill_id.startswith(f"{self.modid}:skill/"):
            skill_id = skill_id.split('/')[-1]
        res = self.dao.update_skill(skill_id, skill_data)
        if res:
            for key in ['name', 'description']:
                lang_key = f"{self.modid}.skill.{skill_id}.{key}"
                dao.LangDao.set_lang(self.modid, lang_key, skill_data.get(key, ''))
                skill_data[key] = lang_key
        return res

    def delete_skill(self, skill_id):
        if skill_id.startswith(f"{self.modid}:skill/"):
            skill_id = skill_id.split('/')[-1]
        res = self.dao.delete_skill(skill_id)
        if res:
            lang_keys = [
                f"{self.modid}.skill.{skill_id}.{key}"
                for key in ['name', 'description']
            ]
            dao.LangDao.del_lang(self.modid, lang_keys)
            dao.LangDao.remove_lang_key(self.modid, lang_keys)
        return res
    
class EventService:
    def __init__(self, modid):
        self.modid = modid
        self.dao = dao.EventDao(modid)

    def get_all_events(self) -> list[dict]:
        event_ids = self.dao.get_all_event_ids()
        events = []
        for eid in event_ids:
            event = self.get_event_by_id(eid)
            if event:
                events.append(event)
        return events

    def get_event_by_id(self, event_id):
        if event_id.startswith(f"{self.modid}:event/"):
            event_id = event_id.split('/')[-1]
        return self.dao.get_event_by_id(event_id)

    def create_event(self, event_data):
        event_id = event_data.get('id')
        if event_id.startswith(f"{self.modid}:event/"):
            event_id = event_id.split('/')[-1]
        else:
            event_data['id'] = f"{self.modid}:event/{event_id}"
        print(event_data)
        res = self.dao.create_event(event_id, event_data)
        if res:
            new_keys = []
            for key in ['name', 'description']:
                lang_key = f"{self.modid}.event.{event_id}.{key}"
                event_data[key] = lang_key
                new_keys.append(lang_key)
            for lang_key in new_keys:
                key = lang_key.split('.')[-1]
                dao.LangDao.set_lang(self.modid, lang_key, event_data.get(key, ''))
            dao.LangDao.add_lang_key(self.modid, new_keys)
        return res

    def update_event(self, event_data):
        event_id = event_data.get('id')
        if event_id.startswith(f"{self.modid}:event/"):
            event_id = event_id.split('/')[-1]
        res = self.dao.update_event(event_id, event_data)
        if res:
            for key in ['name', 'description']:
                lang_key = f"{self.modid}.event.{event_id}.{key}"
                dao.LangDao.set_lang(self.modid, lang_key, event_data.get(key, ''))
                event_data[key] = lang_key
        return res

    def delete_event(self, event_id):
        if event_id.startswith(f"{self.modid}:event/"):
            event_id = event_id.split('/')[-1]
        res = self.dao.delete_event(event_id)
        if res:
            lang_keys = [
                f"{self.modid}.event.{event_id}.{key}"
                for key in ['name', 'description']
            ]
            dao.LangDao.del_lang(self.modid, lang_keys)
            dao.LangDao.remove_lang_key(self.modid, lang_keys)
        return res

class BuffService:
    def __init__(self, modid):
        self.modid = modid
        self.dao = dao.BuffDao(modid)

    def get_all_buffs(self) -> list[dict]:
        buff_ids = self.dao.get_all_buff_ids()
        buffs = []
        for bid in buff_ids:
            buff = self.get_buff_by_id(bid)
            if buff:
                buffs.append(buff)
        return buffs

    def get_buff_by_id(self, buff_id):
        if buff_id.startswith(f"{self.modid}:buff/"):
            buff_id = buff_id.split('/')[-1]
        return self.dao.load_buff_by_id(buff_id)

    def create_buff(self, buff_data):
        buff_id = buff_data.get('id')
        if buff_id.startswith(f"{self.modid}:buff/"):
            buff_id = buff_id.split('/')[-1]
        else:
            buff_data['id'] = f"{self.modid}:buff/{buff_id}"
        res = self.dao.create_buff(buff_id, buff_data)
        if res:
            new_keys = []
            for key in ['name', 'description']:
                lang_key = f"{self.modid}.buff.{buff_id}.{key}"
                buff_data[key] = lang_key
                new_keys.append(lang_key)
            for lang_key in new_keys:
                key = lang_key.split('.')[-1]
                dao.LangDao.set_lang(self.modid, lang_key, buff_data.get(key, ''))
            dao.LangDao.add_lang_key(self.modid, new_keys)
        return res

    def update_buff(self, buff_data):
        buff_id = buff_data.get('id')
        if buff_id.startswith(f"{self.modid}:buff/"):
            buff_id = buff_id.split('/')[-1]
        res = self.dao.update_buff(buff_id, buff_data)
        if res:
            new_keys = []
            for key in ['name', 'description']:
                lang_key = f"{self.modid}.buff.{buff_id}.{key}"
                buff_data[key] = lang_key
                new_keys.append(lang_key)
            for lang_key in new_keys:
                key = lang_key.split('.')[-1]
                dao.LangDao.set_lang(self.modid, lang_key, buff_data.get(key, ''))
            dao.LangDao.add_lang_key(self.modid, new_keys)
        return res

    def delete_buff(self, buff_id):
        if buff_id.startswith(f"{self.modid}:buff/"):
            buff_id = buff_id.split('/')[-1]
        res = self.dao.delete_buff(buff_id)
        if res:
            lang_keys = [
                f"{self.modid}.buff.{buff_id}.{key}"
                for key in ['name', 'description']
            ]
            dao.LangDao.del_lang(self.modid, lang_keys)
            dao.LangDao.remove_lang_key(self.modid, lang_keys)
        return res

if __name__ == "__main__":
    pass

