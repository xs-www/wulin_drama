import json, sys, os
from pathlib import Path
from logger import log
import zipfile

BASE_DIR = Path(__file__).resolve().parent

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_all_mods():
    mods_path = BASE_DIR / "mods"
    if not mods_path.exists():
        mods_path.mkdir(parents=True, exist_ok=True)
    return [f.name for f in mods_path.iterdir() if f.is_dir()]

def get_all_json_file_names(file_path):
    res = []
    if not file_path.exists():
        log.console(f"Data path does not exist: {file_path}", "WARN")
        return res
    res = [f.stem for f in file_path.glob('*.json') if f.is_file()]
    return res

def get_language(modid):
    manifest = ModDao(modid).load_manifest()
    return manifest.get("preferred_language", "zh_cn")

class ModDao:

    def __init__(self, modid):
        self.modid = modid
        self.mod_path = BASE_DIR / "mods" / modid

    def load_manifest(self):
        file_path = self.mod_path / 'manifest.json'
        return load_json(file_path)

    def update_manifest(self, manifest_data):
        file_path = self.mod_path / 'manifest.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, ensure_ascii=False, indent=2)
        log.console(f"Manifest updated for mod: {self.modid}", "INFO")

    def init_mod_directory(self):
        if not self.mod_path.exists():
            self.mod_path.mkdir(parents=True, exist_ok=True)
            # 初始化manifest.json
            default_manifest = load_json(BASE_DIR / 'data' / 'default_manifest.json')
            default_manifest['id'] = self.modid
            self.update_manifest(default_manifest)
            # 初始化export_ignore文件
            export_ignore = load_json(BASE_DIR / 'data' / 'export_ignore.json')
            with open(self.mod_path / 'export_ignore.json', 'w', encoding='utf-8') as f:
                json.dump(export_ignore, f, ensure_ascii=False, indent=2)
            # 初始化assets/lang文件夹
            (self.mod_path / 'assets/lang').mkdir(parents=True, exist_ok=True)
            LangDao.create_lang_file(self.modid, 'zh_cn')
            # 初始化角色文件夹
            char_dao = CharacterDao(self.modid)
            default_char = load_json(BASE_DIR / 'data' / 'default_character.json')
            char_dao.create_character(default_char)
            skill_dao = SkillDao(self.modid)
            buff_dao = BuffDao(self.modid)
            log.console(f"Mod directory created at: {self.mod_path}", "INFO")
        else:
            log.console(f"Mod directory already exists at: {self.mod_path}", "INFO")

    def export_mod(self, export_path = None) -> Path:
        """
        把 mod_root 目录下不在 export_ignore.json 列表中的文件打成 zip。
        返回生成的 zip 路径。
        """
        mod_root = self.mod_path.resolve()
        if not mod_root.is_dir():
            raise ValueError(f"{mod_root} 不是有效目录")

        # 1. 读取忽略列表
        ignore_file = mod_root / "export_ignore.json"
        ignore_set: set[str] = set()
        if ignore_file.is_file():
            try:
                with ignore_file.open("r", encoding="utf-8") as f:
                    ignore_set = set(json.load(f))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"警告：忽略列表读取失败 {e}", file=sys.stderr)

        # 2. 收集需要打包的文件
        to_pack: list[Path] = []
        for p in mod_root.rglob("*"):
            if p.is_file() and p.relative_to(mod_root).as_posix() not in ignore_set:
                to_pack.append(p)

        # 3. 写 zip
        export_path = export_path or (BASE_DIR / "exports" / f"{self.modid}.zip")
        export_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(export_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file in to_pack:
                arcname = file.relative_to(mod_root).as_posix()
                zf.write(file, arcname)
        return export_path

class LangDao:

    def __init__(self, modid, lang='zh_cn'):
        self.file_path = BASE_DIR / "mods" / modid / f'assets/lang/{lang}.json'

    def load_lang(self):
        # log.console(f"加载语言文件: {self.file_path}", "INFO")
        return load_json(self.file_path)

    @staticmethod
    def set_lang(modid, keys, values):
        lang_dao = LangDao(modid)
        lang_data = lang_dao.load_lang()
        if not isinstance(keys, list):
            keys = [keys]
        if not isinstance(values, list):
            values = [values]
        for key, value in zip(keys, values):
            lang_data[key] = value
        with open(lang_dao.file_path, 'w', encoding='utf-8') as f:
            json.dump(lang_data, f, ensure_ascii=False, indent=2)
        log.console(f"设置语言键 '{key}' 为 '{value}'", "INFO")
    
    @staticmethod
    def del_lang(modid, keys):
        lang_dao = LangDao(modid)
        lang_data = lang_dao.load_lang()
        if isinstance(keys, str):
            keys = [keys]
        for key in keys:
            if key in lang_data:
                del lang_data[key]
                with open(lang_dao.file_path, 'w', encoding='utf-8') as f:
                    json.dump(lang_data, f, ensure_ascii=False, indent=2)
                log.console(f"删除语言键 '{key}'", "INFO")
            else:
                log.console(f"语言键 '{key}' 不存在，无法删除", "WARN")

    @staticmethod
    def create_lang_file(modid, lang='zh_cn'):
        lang_path = BASE_DIR / "mods" / modid / f'assets/lang/{lang}.json'
        if not lang_path.exists():
            with open(lang_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            log.console(f"创建新语言文件: {lang_path}", "INFO")
        else:
            log.console(f"Language file already exists: {lang_path}", "INFO")

    @staticmethod
    def add_lang_key(modid, keys: list[str] | str):
        keys_path = BASE_DIR / "mods" / modid / 'assets/lang/lang_keys.json'
        if not keys_path.exists():
            with open(keys_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        lang_keys = load_json(keys_path)
        if isinstance(keys, str):
            keys = [keys]
        for k in keys:
            if k not in lang_keys:
                lang_keys.append(k)
                log.console(f"Added new language key: {k}", "INFO")
        with open(keys_path, 'w', encoding='utf-8') as f:
            json.dump(lang_keys, f, ensure_ascii=False, indent=2)

    @staticmethod
    def remove_lang_key(modid, keys: list[str]):
        keys_path = BASE_DIR / "mods" / modid / 'assets/lang/lang_keys.json'
        if not keys_path.exists():
            log.console(f"Language keys file does not exist: {keys_path}", "WARN")
            return
        lang_keys = load_json(keys_path)
        for key in keys:
            if key in lang_keys:
                lang_keys.remove(key)
                log.console(f"Removed language key: {key}", "INFO")
        with open(keys_path, 'w', encoding='utf-8') as f:
            json.dump(lang_keys, f, ensure_ascii=False, indent=2)

def t(modid, lang, key):
    """
    根据 modid 和 lang 加载对应的语言文件，返回 key 对应的翻译文本。
    如果找不到对应的翻译，则返回 key 本身。
    :param modid: 模组ID
    :param lang: 语言代码，如 'zh_cn'
    :param key: 需要翻译的文本键
    :return: 翻译后的文本或原始键
    """
    lang_dao = LangDao(modid, lang)
    lang_data = lang_dao.load_lang()
    return lang_data.get(key, key)

class CharacterDao:

    def __init__(self, modid):
        self.modid = modid
        self.file_path = BASE_DIR / "mods" / modid / 'data/characters/'

        if not self.file_path.exists():
            self.file_path.mkdir(parents=True, exist_ok=True)

    def get_all_character_ids(self):
        res = []
        if not self.file_path.exists():
            log.console(f"角色文件夹不存在: {self.file_path}", "WARN")
            return res
        log.console(f"加载角色ID: {self.file_path}", "INFO")
        res = [f.stem for f in self.file_path.glob('*.json') if f.is_file()]
        return res

    def get_character_by_id(self, char_id=None):
        res = None
        if char_id:
            log.console(f"加载角色数据: {char_id}", "INFO")
            res = load_json(self.file_path / f'{char_id}.json')
            return res
        log.console("未提供角色ID进行加载。", "WARN")
        return res

    def get_default_character(self):
        return self.get_character_by_id("default_character")

    def create_character(self, char_data):
        char_id = char_data.get('id')
        if not char_id:
            log.console("角色数据必须包含 'id' 字段。", "ERROR")
            return False
        file_path = self.file_path / f'{char_id}.json'
        if file_path.exists():
            log.console(f"角色ID {char_id} 已存在。", "ERROR")
            return False
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(char_data, f, ensure_ascii=False, indent=2)
        log.console(f"角色创建成功，ID: {char_id}", "INFO")
        return True

    def update_character(self, char_id, char_data):
        file_path = self.file_path / f'{char_id}.json'
        if not file_path.exists():
            log.console(f"Character with ID {char_id} does not exist for update.", "ERROR")
            return False
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(char_data, f, ensure_ascii=False, indent=2)
        log.console(f"Character updated with ID: {char_id}", "INFO")
        return True

    def delete_character(self, char_id):
        file_path = self.file_path / f'{char_id}.json'
        if not file_path.exists():
            log.console(f"Character with ID {char_id} does not exist for deletion.", "ERROR")
            return False
        os.remove(file_path)
        log.console(f"Character deleted with ID: {char_id}", "INFO")
        return True
    
class SkillDao:
    
    def __init__(self, modid):
        self.file_path = BASE_DIR / "mods" / modid / 'data/skills/'

        if not self.file_path.exists():
            self.file_path.mkdir(parents=True, exist_ok=True)

    def get_all_skill_ids(self):
        res = []
        if not self.file_path.exists():
            log.console(f"Skill data path does not exist: {self.file_path}", "WARN")
            return res
        res = [f.stem for f in self.file_path.glob('*.json') if f.is_file()]
        return res

    def load_skill_by_id(self, skill_id=None):
        res = None
        if skill_id:
            log.console(f"Loading skill data for ID: {skill_id}", "INFO")
            res = load_json(self.file_path / f'{skill_id}.json')
        log.console(f"Skill data loaded for ID: {skill_id}", "INFO")
        return res

class BuffDao:
    
    def __init__(self, modid):
        self.file_path = BASE_DIR / "mods" / modid / 'data/buffs/'

        if not self.file_path.exists():
            self.file_path.mkdir(parents=True, exist_ok=True)

    def get_all_buff_ids(self):
        res = []
        if not self.file_path.exists():
            log.console(f"Buff data path does not exist: {self.file_path}", "WARN")
            return res
        res = [f.stem for f in self.file_path.glob('*.json') if f.is_file()]
        return res

    def load_buff_by_id(self, buff_id=None):
        if buff_id:
            log.console(f"Loading buff data for ID: {buff_id}", "INFO")
            return load_json(self.file_path / f'{buff_id}.json')
        log.console("No buff ID provided for loading.", "WARN")
        return None

if __name__ == '__main__':
    moddao = ModDao("test")
    moddao.export_mod()