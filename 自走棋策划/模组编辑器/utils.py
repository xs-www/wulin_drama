from rich.console import Console
import uuid, os, re
from datetime import datetime

_term_console = Console()

from pathlib import Path

# 当前正在执行的 .py 文件绝对目录
BASE_DIR = Path(__file__).resolve().parent

def timestampDate():
    """
    获取当前时间戳，格式为 "YYYY-MM-DD"。
    :return: 当前时间戳字符串
    """
    return datetime.now().strftime("%Y-%m-%d")

def timestampTime():
    """
    获取当前时间戳，格式为 "YYYY-MM-DD/HH:MM:SS"。
    :return: 当前时间戳字符串
    """
    return datetime.now().strftime("%Y-%m-%d/%H:%M:%S")

class Entry:

    def __init__(self, content: str, info_type: str = "INFO", timestamp: str = None):
        self.content = content
        self.timestamp = timestamp if timestamp is not None else timestampTime()
        self.info_type = info_type

    def __str__(self):
        """给文件用的纯文本"""
        return f"[{self.timestamp}] [{self.info_type}] {self.content}"
    
    def rich_str(self):
        """给终端用的富文本，带颜色标签"""
        color_map = {"INFO": "cyan", "WARN": "yellow", "ERROR": "bold red", "OK": "bold green"}
        color = color_map.get(self.info_type, "white")
        return f"[{color}][{self.timestamp}] [{self.info_type}][/{color}] {self.content}"

class Logger:
    def __init__(self):
        self.entries: list[Entry] = []

    def console(self, content: str, info_type: str = "INFO") -> bool:
        entry = Entry(content, info_type)
        _term_console.print(entry.rich_str())   # ① 终端走 rich
        self.addEntry(entry)                    # ② 文件走 __str__
        return True
    
    def clearLog(self):
        self.entries = []
    
    def addEntry(self, entry: Entry):
        self.entries.append(entry)
        if len(self.entries) > 1000:
            self.saveLog()
        return True
    
    def getLog(self) -> list:
        return self.entries
    
    # 追加日志到文件尾
    def saveLog(self, file_path: str = None):
        log.console("保存日志...", "INFO")
        log.entries.pop(-1) # 移除最后一条“保存日志...”记录
        if file_path is None:
            file_path = f"{BASE_DIR}/logs/editor_log_{timestampDate()}.txt"

        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        with open(file_path, 'a', encoding='utf-8') as file:
            for entry in self.entries:
                file.write(str(entry) + "\n")
        log.console(f"日志已保存到：{file_path}", "INFO")
        self.clearLog()

log = Logger()

def effect_parser(effect_dict: dict) -> str:
    """
    解析效果字典为自然语言形式。
    例如:
    {
        "type": "modify_attr",
        "param": "MHP+10",
        "mode": "all_ally"
    }
    ->
    "所有右方单位生命上限+10“
    :param effect_str: 效果字符串
    :return: 效果描述
    """

    try:
        if effect_dict.get("type") == "modify_attr":
            param = effect_dict.get("param", "")
            mode = effect_dict.get("mode", "")
            target_map = {
                "all_ally": "所有右方单位",
                "all_enemy": "所有左方单位",
                "self": "自身",
            }
            target_desc = target_map.get(mode, "未知目标")
            return f"{target_desc}{param.replace('+', '增加').replace('-', '减少')}"
    except Exception as e:
        log.console(f"解析效果失败: {e}", "ERROR")
        return "格式错误，请检查输入"
    
def parse_param(effect_type: str, param: str) -> dict:
    """
    解析效果参数字符串，返回结构化信息
    :return: 解析后的信息字典
    """
    ATTRS = {
        "ATK": "攻击力",
        "MHP": "最大生命值",
        "HP": "生命值",
        "DMG": "伤害",
        "SPD": "速度",
        "SPEED": "速度",
        "NRG": "能量",
        "ENERGY": "能量",
        "HATE": "仇恨值",
        "CRTRA": "暴击率",
        "CRTDMG": "暴击伤害"
    }
    match effect_type:
        case "modify_attr":
            pattern = re.compile(
                r'(?P<attr>[A-Z]+)'          # 1. 属性：任意大写字母串
                r'(?P<op>[+-=])'              # 2. 方向：+ 或 -
                r'(?P<val>[1-9]\d*)'         # 3. 数值：正整数（首位不能为 0）
                r'(?:(?P<is_pct>%)(?P<pct_base>[bmr]))?'  # 4. 可选：% 紧跟 b/m/r
            )
            info = pattern.fullmatch(param).groupdict()
            info['attr'] = ATTRS.get(info['attr'])
            info['is_pct'] = True if info['is_pct'] else False
            if info['is_pct']:
                if info['pct_base'] == 'm' and info['attr'] not in ['hp', 'energy']:
                    info['pct_base'] = 'r'  # 非生命和能量属性，m视为r
                elif not info['pct_base']:
                    info['pct_base'] = 'r'  # 默认百分比基于当前值
                info['pct_base_desc'] = {
                    'b': '基础值',
                    'm': '最大值',
                    'r': '当前值'
                }.get(info['pct_base'], '当前值')
            return info
        case "add_buff":
            pass
        case "remove_buff":
            pass
        case "add_statu":
            pass
        case "remove_statu":
            pass
        case _:
            pass
