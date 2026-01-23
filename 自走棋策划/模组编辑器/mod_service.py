import mod_dao as dao
from utils import effect_parser, parse_data_id, t, translate_data
import re, shutil
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent

def get_id_path(data_id):
    modid, data_type, data_id = parse_data_id(data_id)
    return Path(modid) / data_type / f"{data_id}.json"

def gen_data_id(data_id, data_type=None, modid=None):
    if not modid or not data_type:
        raise ValueError("modid 和 data_type 不能为空")
    if ':' not in data_id:
        short_id = data_id
        long_id = f"{modid}:{data_type}/{short_id}"
    else:
        short_id = data_id.split('/')[-1]
        long_id = data_id
    return short_id, long_id

class ModService:
    def __init__(self, modid):
        self.modid = modid
        self.dao = dao.ModDao(modid)

    def init_directory(self):
        res = self.dao.init_mod_directory()
        src = BASE_PATH / 'data' / 'WuLinXi'
        dst = self.dao.mod_path / 'data' / 'WuLinXi'
        shutil.copytree(src, dst, dirs_exist_ok=True)
        return res
    
    def export_mod(self, export_path=None):
        return self.dao.export_mod(export_path)

    def save_data(self, data_dict):
        data_id = data_dict.get('id')
        modid, data_type, data_id = parse_data_id(data_id)
        data_file_path = self.dao.mod_path / 'data' / modid / data_type / f"{data_id}.json"
        dao.save_data_to_file(data_file_path, data_dict)
        return True

    def load_all_data(self, data_type, is_self_mod=False):
        data_type = data_type.lower() + 's'
        mod_list = dao.get_dirs_in_directory(self.dao.mod_path / 'data') if not is_self_mod else [self.modid]
        data_list = []
        for modid in mod_list:
            mod_data = dao.load_data_from_dir(self.dao.mod_path / 'data' / modid / data_type)
            data_list.extend(mod_data)
        return data_list
    
    def load_data_by_id(self, data_id):
        modid, data_type, data_id = parse_data_id(data_id)
        data_file_path = self.dao.mod_path / 'data' / modid / data_type / f"{data_id}.json"
        return dao.load_data_from_file(data_file_path)

    def delete_data(self, data_id):
        modid, data_type, data_id = parse_data_id(data_id)
        data_file_path = self.dao.mod_path / 'data' / modid / data_type / f"{data_id}.json"
        return dao.delete_file(data_file_path)

class CharacterService:
    def __init__(self, modid):
        self.modid = modid
        self.dao = dao.CharacterDao(modid)
        self.mod_service = ModService(modid)

    def get_all_character(self, is_self_mod=False):
        characters = self.mod_service.load_all_data('character', is_self_mod=is_self_mod)
        for i, char in enumerate(characters):
            characters[i] = translate_data(self.modid, char)
        return characters

    def get_character_by_id(self, char_id):
        _, char_id = gen_data_id(char_id, data_type='character', modid=self.modid)
        char_data = self.mod_service.load_data_by_id(char_id)
        char_data = translate_data(self.modid, char_data)
        return char_data

    def create_character(self, char_data):
        char = dao.get_default_data('character')
        trans = {}
        char_id, char_data['id'] = gen_data_id(char_data.get('id'), data_type='character', modid=self.modid)

        for key in char:
            if key in ['name', 'background', 'description']:
                lang_key = f"{self.modid}.character.{char_id}.{key}"
                char[key] = lang_key
                trans[lang_key] = char_data.get(key, '')
            else:
                if key in char_data:
                    char[key] = char_data[key]
        res = self.mod_service.save_data(char)
        if res:
            for lang_key, value in trans.items():
                dao.LangDao.set_lang(self.modid, lang_key, value)
            dao.LangDao.add_lang_key(self.modid, list(trans.keys()))
        return res

    def update_character(self, char_data):
        char_id, char_data['id'] = gen_data_id(char_data.get('id'), data_type='character', modid=self.modid)
        trans = {}
        for key in ['name', 'background', 'description']:
            lang_key = f"{self.modid}.character.{char_id}.{key}"
            trans[lang_key] = char_data.get(key, '')
            char_data[key] = lang_key
        res = self.mod_service.save_data(char_data)
        if res:
            for lang_key, value in trans.items():
                dao.LangDao.set_lang(self.modid, lang_key, value)
        return res

    def delete_character(self, char_id):
        char_id, full_id = gen_data_id(char_id, data_type='character', modid=self.modid)
        res = self.mod_service.delete_data(full_id)
        if res:
            lang_keys = [
                f"{self.modid}.character.{char_id}.{key}"
                for key in ['name', 'background', 'description']
            ]
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
        self.mod_service = ModService(modid)

    def get_all_factions(self, is_self_mod=False) -> list[dict]:
        factions = self.mod_service.load_all_data('faction', is_self_mod=is_self_mod)
        for i, faction in enumerate(factions):
            factions[i] = translate_data(self.modid, faction)
        return factions
    
    def get_faction_by_id(self, faction_id):
        _, faction_id = gen_data_id(faction_id, data_type='faction', modid=self.modid)
        faction_data = self.mod_service.load_data_by_id(faction_id)
        faction_data = translate_data(self.modid, faction_data)
        return faction_data

    def create_faction(self, faction_data):
        faction = dao.get_default_data('faction')
        faction['effects'] = {}
        faction_id, faction_data['id'] = gen_data_id(faction_data.get('id'), data_type='faction', modid=self.modid)
        trans = {}
        for key in faction:
            if key in ['name', 'description']:
                lang_key = f"{self.modid}.faction.{faction_id}.{key}"
                faction[key] = lang_key
                trans[lang_key] = faction_data.get(key, '')
            else:
                if key in faction_data:
                    faction[key] = faction_data[key]
        res = self.mod_service.save_data(faction)
        if res:
            for lang_key, value in trans.items():
                dao.LangDao.set_lang(self.modid, lang_key, value)
            dao.LangDao.add_lang_key(self.modid, list(trans.keys()))
        return res

    def update_faction(self, faction_data):
        faction_id, faction_data['id'] = gen_data_id(faction_data.get('id'), data_type='faction', modid=self.modid)
        trans = {}
        for key in ['name', 'description']:
            lang_key = f"{self.modid}.faction.{faction_id}.{key}"
            trans[lang_key] = faction_data.get(key, '')
            faction_data[key] = lang_key
        res = self.mod_service.save_data(faction_data)
        if res:
            for lang_key, value in trans.items():
                dao.LangDao.set_lang(self.modid, lang_key, value)
        return res

    def save_faction(self, faction_dict):
        _, full_id = gen_data_id(faction_dict.get('id'), data_type='faction', modid=self.modid)
        path = self.mod_service.dao.mod_path / get_id_path(full_id)
        if dao.has_file(path):
            return self.update_faction(faction_dict)
        else:
            return self.create_faction(faction_dict)

    def delete_faction(self, faction_id):
        faction_id, full_id = gen_data_id(faction_id, data_type='faction', modid=self.modid)
        res = self.mod_service.delete_data(full_id)
        if res:
            lang_keys = [
                f"{self.modid}.faction.{faction_id}.{key}"
                for key in ['name', 'description']
            ]
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
        self.mod_service = ModService(modid)

    def get_all_skills(self, is_self_mod=False) -> list[dict]:
        skills = self.mod_service.load_all_data('skill', is_self_mod=is_self_mod)
        for i, skill in enumerate(skills):
            skills[i] = translate_data(self.modid, skill)
        return skills
    
    def get_skill_by_id(self, skill_id):
        _, skill_id = gen_data_id(skill_id, data_type='skill', modid=self.modid)
        skill_data = self.mod_service.load_data_by_id(skill_id)
        skill_data = translate_data(self.modid, skill_data)
        return skill_data

    def create_skill(self, skill_data):
        skill_id, skill_data['id'] = gen_data_id(skill_data.get('id'), data_type='skill', modid=self.modid)
        trans = {}
        for key in ['name', 'description']:
            lang_key = f"{self.modid}.skill.{skill_id}.{key}"
            trans[lang_key] = skill_data.get(key, '')
        res = self.mod_service.save_data(skill_data)
        if res:
            for lang_key, value in trans.items():
                dao.LangDao.set_lang(self.modid, lang_key, value)
            dao.LangDao.add_lang_key(self.modid, list(trans.keys()))
        return res

    def update_skill(self, skill_data):
        skill_id, skill_data['id'] = gen_data_id(skill_data.get('id'), data_type='skill', modid=self.modid)
        trans = {}
        for key in ['name', 'description']:
            lang_key = f"{self.modid}.skill.{skill_id}.{key}"
            trans[lang_key] = skill_data.get(key, '')
            skill_data[key] = lang_key
        res = self.mod_service.save_data(skill_data)
        if res:
            for lang_key, value in trans.items():
                dao.LangDao.set_lang(self.modid, lang_key, value)
        return res

    def delete_skill(self, skill_id):
        _, skill_id = gen_data_id(skill_id, data_type='skill', modid=self.modid)
        res = self.mod_service.delete_data(skill_id)
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
        #self.dao = dao.EventDao(modid)
        self.mod_service = ModService(modid)

    def get_all_events(self, is_self_mod=False) -> list[dict]:
        events = self.mod_service.load_all_data('event', is_self_mod=is_self_mod)
        for i, event in enumerate(events):
            events[i] = translate_data(self.modid, event)
        return events

    def get_event_by_id(self, event_id):
        _, event_id = gen_data_id(event_id, data_type='event', modid=self.modid)
        event_data = self.mod_service.load_data_by_id(event_id)
        event_data = translate_data(self.modid, event_data)
        return event_data

    def create_event(self, event_data):
        event_id, event_data['id'] = gen_data_id(event_data.get('id'), data_type='event', modid=self.modid)
        trans = {}
        for key in ['name', 'description']:
            lang_key = f"{self.modid}.event.{event_id}.{key}"
            trans[lang_key] = event_data.get(key, '')
            event_data[key] = lang_key
        res = self.mod_service.save_data(event_data)
        if res:
            for lang_key, value in trans.items():
                dao.LangDao.set_lang(self.modid, lang_key, value)
            dao.LangDao.add_lang_key(self.modid, list(trans.keys()))
        return res

    def update_event(self, event_data):
        event_id, event_data['id'] = gen_data_id(event_data.get('id'), data_type='event', modid=self.modid)
        trans = {}
        for key in ['name', 'description']:
            lang_key = f"{self.modid}.event.{event_id}.{key}"
            trans[lang_key] = event_data.get(key, '')
            event_data[key] = lang_key
        res = self.mod_service.save_data(event_data)
        if res:
            for lang_key, value in trans.items():
                dao.LangDao.set_lang(self.modid, lang_key, value)
        return res

    def delete_event(self, event_id):
        _, event_id = gen_data_id(event_id, data_type='event', modid=self.modid)
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
        self.mod_service = ModService(modid)

    def get_all_buffs(self, is_self_mod=False) -> list[dict]:
        buffs = self.mod_service.load_all_data('buff', is_self_mod=is_self_mod)
        for i, buff in enumerate(buffs):
            buffs[i] = translate_data(self.modid, buff)
        return buffs

    def get_buff_by_id(self, buff_id):
        _, buff_id = gen_data_id(buff_id, data_type='buff', modid=self.modid)
        buff_data = self.mod_service.load_data_by_id(buff_id)
        buff_data = translate_data(self.modid, buff_data)
        return buff_data

    def create_buff(self, buff_data):
        buff_id, buff_data['id'] = gen_data_id(buff_data.get('id'), data_type='buff', modid=self.modid)
        trans = {}
        for key in ['name', 'description']:
            lang_key = f"{self.modid}.buff.{buff_id}.{key}"
            trans[lang_key] = buff_data.get(key, '')
            buff_data[key] = lang_key
        res = self.mod_service.save_data(buff_data)
        if res:
            for lang_key, value in trans.items():
                dao.LangDao.set_lang(self.modid, lang_key, value)
        return res

    def update_buff(self, buff_data):
        buff_id, buff_data['id'] = gen_data_id(buff_data.get('id'), data_type='buff', modid=self.modid)
        trans = {}
        for key in ['name', 'description']:
            lang_key = f"{self.modid}.buff.{buff_id}.{key}"
            trans[lang_key] = buff_data.get(key, '')
            buff_data[key] = lang_key
        res = self.mod_service.save_data(buff_data)
        if res:
            for lang_key, value in trans.items():
                dao.LangDao.set_lang(self.modid, lang_key, value)
        return res

    def delete_buff(self, buff_id):
        _, buff_id = gen_data_id(buff_id, data_type='buff', modid=self.modid)
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
    ms = ModService('test')
    print(ms.load_all_data('character'))

