import json, sys, os
from pathlib import Path
from utils import log
import zipfile, shutil
import fnmatch

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
        log.console(f"数据路径不存在: {file_path}", "WARN")
        return res
    res = [f.stem for f in file_path.glob('*.json') if f.is_file()]
    return res

def get_default_language(modid):
    manifest = ModDao(modid).load_manifest()
    return manifest.get("preferred_language", "zh_cn")

def get_default_data(data_type):
    data = load_json(BASE_DIR / 'data' / f'default_{data_type}.json')
    return data

def save_data_to_file(data_file_path: Path, data_dict: dict):
    data_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(data_file_path, 'w', encoding='utf-8') as f:
        json.dump(data_dict, f, ensure_ascii=False, indent=2)
    log.console(f"数据已保存到文件: {data_file_path}", "INFO")

def load_data_from_file(data_file_path: Path) -> dict:
    if not data_file_path.exists():
        log.console(f"数据文件不存在: {data_file_path}", "WARN")
        return {}
    data = load_json(data_file_path)
    log.console(f"已加载数据 from {data_file_path}", "INFO")
    return data

def delete_file(file_path: Path):
    if file_path.exists():
        file_path.unlink()
        log.console(f"已删除文件: {file_path}", "INFO")
        return True
    else:
        log.console(f"文件不存在，无法删除: {file_path}", "WARN")
        return False

def load_data_from_dir(data_dir: Path) -> list[dict]:
    data_list = []
    if not data_dir.exists():
        log.console(f"数据目录不存在: {data_dir}", "WARN")
        return data_list
    for file_path in data_dir.glob('*.json'):
        if file_path.is_file():
            data = load_json(file_path)
            data_list.append(data)
    log.console(f"已加载 {len(data_list)} 条数据 from {data_dir}", "INFO")
    return data_list

def get_dirs_in_directory(directory: Path) -> list[str]:
    if not directory.exists():
        log.console(f"目录不存在: {directory}", "WARN")
        return []
    dirs = [f.name for f in directory.iterdir() if f.is_dir()]
    log.console(f"已获取目录列表 from {directory}: {dirs}", "INFO")
    return dirs

def has_file(file_path: Path) -> bool:
    return file_path.exists()

def export_WuLinXi_data():
    modid = "WuLinXi"
    mod_dao = ModDao(modid)
    mod_dao.export_mod()

    src = mod_dao.mod_path / 'data' / 'WuLinXi'
    dst = BASE_DIR / 'data' / 'WuLinXi'
    
    shutil.copytree(src, dst, dirs_exist_ok=True)

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
        log.console(f"配置已更新，模组ID: {self.modid}", "INFO")

    def init_mod_directory(self):
        if not self.mod_path.exists():
            self.mod_path.mkdir(parents=True, exist_ok=True)
            # 初始化manifest.json
            default_manifest = load_json(BASE_DIR / 'data' / 'default_manifest.json')
            default_manifest['id'] = self.modid
            self.update_manifest(default_manifest)
            # 初始化export_ignore文件
            export_ignore = load_json(BASE_DIR / 'data' / 'export_ignore.json')
            for i in range(len(export_ignore)):
                if 'MODID' in export_ignore[i]:
                    export_ignore[i] = export_ignore[i].replace('MODID', self.modid)
            with open(self.mod_path / 'export_ignore.json', 'w', encoding='utf-8') as f:
                json.dump(export_ignore, f, ensure_ascii=False, indent=2)

            # 初始化assets文件夹
            # 初始化assets/lang文件夹
            (self.mod_path / 'assets' / self.modid / 'lang').mkdir(parents=True, exist_ok=True)
            LangDao.create_lang_file(self.modid, 'zh_cn')

            # 初始化data文件夹
            # 初始化角色文件夹
            CharacterDao(self.modid)
            SkillDao(self.modid)
            BuffDao(self.modid)
            FactionDao(self.modid)
            #EventDao(self.modid)
            log.console(f"模组目录已创建，路径: {self.mod_path}", "INFO")

            # 初始化scripts文件夹
            (self.mod_path / 'scripts').mkdir(parents=True, exist_ok=True)

            log.console(f"模组目录已创建，路径: {self.mod_path}", "INFO")
            return True
        else:
            log.console(f"模组目录已存在，路径: {self.mod_path}", "INFO")
            return False

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
        ignore_list: list[str] = []
        if ignore_file.is_file():
            try:
                with ignore_file.open("r", encoding="utf-8") as f:
                    ignore_list = list(json.load(f) or [])
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"警告：忽略列表读取失败 {e}", file=sys.stderr)
        # 预处理模式：替换 MODID 占位符为当前 modid
        patterns = [p.replace('MODID', self.modid) for p in ignore_list]

        # 2. 收集需要打包的文件
        to_pack: list[Path] = []
        for p in mod_root.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(mod_root).as_posix()
            # 路径相对于 mod_root，与 patterns 做 fnmatch 通配符匹配
            skip = False
            for pat in patterns:
                try:
                    if fnmatch.fnmatch(rel, pat):
                        skip = True
                        break
                except Exception:
                    # 若模式异常，则忽略该模式
                    continue
            if skip:
                continue

            # 针对 mods/<modid>/data/*/WuLinXi/ 的特殊导出逻辑：
            # 与 BASE_DIR/data/*/WuLinXi/ 对应路径下的同名文件逐个比较，
            # 只有当文件内容不同或基线文件缺失时才将该文件加入待打包列表。
            parts = rel.split('/')
            if len(parts) >= 4 and parts[0] == 'data' and parts[1] == 'WuLinXi':
                base_subdir = parts[2]
                subpath_under_wuxinxi = '/'.join(parts[3:])
                base_file = BASE_DIR / 'data' / 'WuLinXi' / base_subdir / subpath_under_wuxinxi
                try:
                    if base_file.exists():
                        # 比较文件内容
                        if p.read_bytes() == base_file.read_bytes():
                            # 内容相同，跳过导出
                            log.console(f"跳过导出: {rel}", "INFO")
                            continue
                        else:
                            # 内容不同，加入导出列表
                            log.console(f"包含修改文件: {rel}", "INFO")
                            to_pack.append(p)
                            continue
                    else:
                        # 基线文件不存在，加入导出
                        to_pack.append(p)
                        log.console(f"包含新文件: {rel}", "INFO")
                        continue
                except Exception as e:
                    # 发生异常时保守处理：记录并包含文件
                    log.console(f"比较基线文件时出错，包含文件: {p} 错误: {e}", "WARN")
                    to_pack.append(p)
                    continue

            # 非特殊路径或未命中比较规则的文件直接加入待打包列表
            to_pack.append(p)

        # 3. 写 zip
        manifest = self.load_manifest()
        mod_name = f"{manifest.get('id')}-{manifest.get('version', 'unknown')}"
        export_path = export_path or (BASE_DIR / "exports" / f"{mod_name}.zip")
        export_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(export_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file in to_pack:
                arcname = file.relative_to(mod_root).as_posix()
                zf.write(file, arcname)
        return export_path

class LangDao:

    def __init__(self, modid, lang='zh_cn'):
        self.file_path = BASE_DIR / "mods" / modid / 'assets' / modid / f'lang/{lang}.json'

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
            lang_data[key] = str(value)
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
        lang_path = BASE_DIR / "mods" / modid / 'assets' / modid / f'lang/{lang}.json'
        if not lang_path.exists():
            with open(lang_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            log.console(f"创建新语言文件: {lang_path}", "INFO")
        else:
            log.console(f"语言文件已存在: {lang_path}", "INFO")

    @staticmethod
    def add_lang_key(modid, keys: list[str] | str):
        keys_path = BASE_DIR / "mods" / modid / 'assets' / modid / 'lang/lang_keys.json'
        if not keys_path.exists():
            with open(keys_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        lang_keys = load_json(keys_path)
        if isinstance(keys, str):
            keys = [keys]
        for k in keys:
            if k not in lang_keys:
                lang_keys.append(k)
                log.console(f"已添加新的语言键: {k}", "INFO")
        with open(keys_path, 'w', encoding='utf-8') as f:
            json.dump(lang_keys, f, ensure_ascii=False, indent=2)

    @staticmethod
    def remove_lang_key(modid, keys: list[str]):
        keys_path = BASE_DIR / "mods" / modid / 'assets' / modid / 'lang/lang_keys.json'
        if not keys_path.exists():
            log.console(f"语言键文件不存在: {keys_path}", "WARN")
            return
        lang_keys = load_json(keys_path)
        for key in keys:
            if key in lang_keys:
                lang_keys.remove(key)
                log.console(f"已移除语言键: {key}", "INFO")
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
        self.file_path = BASE_DIR / "mods" / modid / 'data' / modid / 'characters/'

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

    def create_character(self, char_id, char_data):
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
            log.console(f"角色ID {char_id} 不存在，无法删除。", "ERROR")
            return False
        os.remove(file_path)
        log.console(f"角色已删除，ID: {char_id}", "INFO")
        return True
    
class SkillDao:
    
    def __init__(self, modid):
        self.modid = modid
        self.file_path = BASE_DIR / "mods" / modid / 'data' / modid / 'skills/'

        if not self.file_path.exists():
            self.file_path.mkdir(parents=True, exist_ok=True)

    def get_all_skill_ids(self):
        res = []
        if not self.file_path.exists():
            log.console(f"技能数据路径不存在: {self.file_path}", "WARN")
            return res
        res = [f.stem for f in self.file_path.glob('*.json') if f.is_file()]
        return res

    def get_skill_by_id(self, skill_id=None):
        res = None
        if skill_id:
            log.console(f"加载技能数据，ID: {skill_id}", "INFO")
            res = load_json(self.file_path / f'{skill_id}.json')
        log.console(f"技能数据加载完成，ID: {skill_id}", "INFO")
        return res

    def create_skill(self, skill_id, skill_data):
        file_path = self.file_path / f'{skill_id}.json'
        if file_path.exists():
            log.console(f"技能ID {skill_id} 已存在。", "ERROR")
            return False
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(skill_data, f, ensure_ascii=False, indent=2)
        log.console(f"技能创建成功，ID: {skill_id}", "INFO")
        return True
    
    def update_skill(self, skill_id, skill_data):
        file_path = self.file_path / f'{skill_id}.json'
        if not file_path.exists():
            log.console(f"技能ID {skill_id} 不存在，无法更新。", "ERROR")
            return False
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(skill_data, f, ensure_ascii=False, indent=2)
        log.console(f"技能更新成功，ID: {skill_id}", "INFO")
        return True

    def delete_skill(self, skill_id):
        file_path = self.file_path / f'{skill_id}.json'
        if not file_path.exists():
            log.console(f"技能ID {skill_id} 不存在，无法删除。", "ERROR")
            return False
        os.remove(file_path)
        log.console(f"技能已删除，ID: {skill_id}", "INFO")
        return True
    
class BuffDao:
    
    def __init__(self, modid):
        self.modid = modid
        self.file_path = BASE_DIR / "mods" / modid / 'data' / modid / 'buffs/'

        if not self.file_path.exists():
            self.file_path.mkdir(parents=True, exist_ok=True)

    def get_all_buff_ids(self):
        res = []
        if not self.file_path.exists():
            log.console(f"Buff数据路径不存在: {self.file_path}", "WARN")
            return res
        res = [f.stem for f in self.file_path.glob('*.json') if f.is_file()]
        return res

    def load_buff_by_id(self, buff_id=None):
        if buff_id:
            log.console(f"加载Buff数据，ID: {buff_id}", "INFO")
            return load_json(self.file_path / f'{buff_id}.json')
        log.console("未提供Buff ID进行加载。", "WARN")
        return None
    
    def create_buff(self, buff_id, buff_data):
        file_path = self.file_path / f'{buff_id}.json'
        if file_path.exists():
            log.console(f"Buff ID {buff_id} 已存在。", "ERROR")
            return False
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(buff_data, f, ensure_ascii=False, indent=2)
        log.console(f"Buff创建成功，ID: {buff_id}", "INFO")
        return True
    
    def update_buff(self, buff_id, buff_data):
        file_path = self.file_path / f'{buff_id}.json'
        if not file_path.exists():
            log.console(f"Buff ID {buff_id} 不存在，无法更新。", "ERROR")
            return False
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(buff_data, f, ensure_ascii=False, indent=2)
        log.console(f"Buff更新成功，ID: {buff_id}", "INFO")
        return True
    
    def delete_buff(self, buff_id):
        file_path = self.file_path / f'{buff_id}.json'
        if not file_path.exists():
            log.console(f"Buff ID {buff_id} 不存在，无法删除。", "ERROR")
            return False
        os.remove(file_path)
        log.console(f"Buff已删除，ID: {buff_id}", "INFO")
        return True
    
class FactionDao:

    def __init__(self, modid):
        self.modid = modid
        self.file_path = BASE_DIR / "mods" / modid / 'data' / modid / 'factions/'

        if not self.file_path.exists():
            self.file_path.mkdir(parents=True, exist_ok=True)
    
    def get_all_faction_ids(self):
        res = []
        if not self.file_path.exists():
            log.console(f"羁绊数据路径不存在: {self.file_path}", "WARN")
            return res
        res = [f.stem for f in self.file_path.glob('*.json') if f.is_file()]
        return res
    
    def get_faction_by_id(self, faction_id=None):
        if faction_id:
            log.console(f"加载羁绊数据，ID: {faction_id}", "INFO")
            return load_json(self.file_path / f'{faction_id}.json')
        log.console("未提供羁绊ID进行加载。", "WARN")
        return None
    
    def create_faction(self, faction_id, faction_data):
        file_path = self.file_path / f'{faction_id}.json'
        if not self.file_path.exists():
            print(f"Creating faction data directory: {self.file_path}")
            self.file_path.mkdir(parents=True, exist_ok=True)
        if file_path.exists():
            log.console(f"羁绊ID {faction_id} 已存在。", "ERROR")
            return False
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(faction_data, f, ensure_ascii=False, indent=2)
        log.console(f"羁绊创建成功，ID: {faction_id}", "INFO")
        return True

    def update_faction(self, faction_id, faction_data):
        file_path = self.file_path / f'{faction_id}.json'
        if not file_path.exists():
            log.console(f"羁绊ID {faction_id} 不存在，无法更新。", "ERROR")
            return False
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(faction_data, f, ensure_ascii=False, indent=2)
        log.console(f"羁绊更新成功，ID: {faction_id}", "INFO")
        return True

    def delete_faction(self, faction_id):
        file_path = self.file_path / f'{faction_id}.json'
        if not file_path.exists():
            log.console(f"羁绊ID {faction_id} 不存在，无法删除。", "ERROR")
            return False
        os.remove(file_path)
        log.console(f"羁绊已删除，ID: {faction_id}", "INFO")
        return True

    def get_all_event_ids(self):
        res = []
        if not self.file_path.exists():
            log.console(f"事件数据路径不存在: {self.file_path}", "WARN")
            return res
        res = [f.stem for f in self.file_path.glob('*.json') if f.is_file()]
        return res

    def get_event_by_id(self, event_id=None):
        if event_id:
            log.console(f"加载事件数据，ID: {event_id}", "INFO")
            return load_json(self.file_path / f'{event_id}.json')
        log.console("未提供事件ID进行加载。", "WARN")
        return None

    def create_event(self, event_id, event_data):
        file_path = self.file_path / f'{event_id}.json'
        if not self.file_path.exists():
            print(f"Creating event data directory: {self.file_path}")
            self.file_path.mkdir(parents=True, exist_ok=True)
        if file_path.exists():
            log.console(f"事件ID {event_id} 已存在。", "ERROR")
            return False
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(event_data, f, ensure_ascii=False, indent=2)
        log.console(f"事件创建成功，ID: {event_id}", "INFO")
        return True

    def update_event(self, event_id, event_data):
        file_path = self.file_path / f'{event_id}.json'
        if not file_path.exists():
            log.console(f"事件ID {event_id} 不存在，无法更新。", "ERROR")
            return False
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(event_data, f, ensure_ascii=False, indent=2)
        log.console(f"事件更新成功，ID: {event_id}", "INFO")
        return True

    def delete_event(self, event_id):
        file_path = self.file_path / f'{event_id}.json'
        if not file_path.exists():
            log.console(f"事件ID {event_id} 不存在，无法删除。", "ERROR")
            return False
        os.remove(file_path)
        log.console(f"事件已删除，ID: {event_id}", "INFO")
        return True

if __name__ == '__main__':
    pass