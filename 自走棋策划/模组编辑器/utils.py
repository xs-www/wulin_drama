from rich.console import Console
import uuid, os, re
from datetime import datetime

_term_console = Console()

from pathlib import Path

# 当前正在执行的 .py 文件绝对目录
BASE_DIR = Path(__file__).resolve().parent

class ParseError(Exception):
    """自定义解析错误异常类"""
    pass

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

    def console(self, content: str, info_type: str = "INFO", record: bool = True) -> bool:
        entry = Entry(content, info_type)
        _term_console.print(entry.rich_str())   # ① 终端走 rich
        if record:
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

ATTRS = {
    "ATK": "攻击力",
    "MHP": "最大生命值",
    "HP": "生命值",
    "DEF": "防御力",
    "DMG": "伤害",
    "SPD": "速度",
    "SPEED": "速度",
    "NRG": "能量",
    "ENERGY": "能量",
    "RECHARGE": "能量恢复效率",
    "RECHG": "能量恢复效率",
    "HTE": "仇恨值",
    "HATE": "仇恨值",
    "CRTRA": "暴击率",
    "CRITRATE": "暴击率",
    "CRTDMG": "暴击伤害",
    "CRITDAMAGE": "暴击伤害",
    "INITIA": "先攻值",
    "INITIATIVE": "先攻值",
}

def effect_parser(effect_dict: dict, highlight_num = False) -> str:
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
        match effect_dict.get("type"):
            case "modify_attr":
                param = effect_dict.get("param", "")
                parsed_param = parse_param("modify_attr", param, highlight_num)
                mode = effect_dict.get("mode", "")
                parsed_mode = parse_mode("modify_attr", mode)
                return f"使{parsed_mode}{parsed_param}"
            case _:
                return "暂不支持该效果类型的解析"
    except Exception as e:
        log.console(f"解析效果失败: {e}", "ERROR", False)
        return "格式错误，请检查输入"
    
def parse_param(effect_type: str, param: str, highlight_num = False) -> dict:
    """
    解析效果参数字符串，返回结构化信息
    :return: 解析后的信息字典
    """

    match effect_type:
        case "modify_attr":
            res = ''
            pattern = re.compile(
                r'(?P<attr>[A-Z]+)'          # 1. 属性：任意大写字母串
                r'(?P<op>[+-=])'             # 2. 方向：+ 或 - 或 =
                r'(?P<val>[1-9]\d*)'        # 3. 数值：正整数（首位不能为 0）
                r'(?:(?P<is_pct>%)(?P<pct_base>[bmrc]))?'  # 4. 可选：% 紧跟 b/m/r/c
                r'(?:\((?P<paren>[A-Z]+)\))?'           # 5. 可选：末尾括号内的大写字母标签，如 (TAG)
            )
            m = pattern.fullmatch(param)
            if not m:
                log.console(f"参数解析失败，无法匹配: {param}", "WARN")
                raise ParseError("参数解析失败, 请检查格式是否正确")
            info = m.groupdict()
            raw_attr = info.get('attr')
            # 将属性代码映射为中文描述，若无对应则保留原代码
            info['attr'] = ATTRS.get(raw_attr, raw_attr)
            if raw_attr in ['HP', 'NRG']:
                info['op'] = {'+': '恢复', '-': '降低', '=': '变为'}.get(info.get('op'), info.get('op'))
            else:
                info['op'] = {'+': '提升', '-': '减少', '=': '变为'}.get(info.get('op'), info.get('op'))
            res += f"{info['attr']}{info['op']}:"
            # 处理百分比标识
            info['is_pct'] = True if info.get('is_pct') else False
            if info['is_pct']:
                if info.get('pct_base') == 'm' and raw_attr not in ['HP', 'MHP', 'NRG', 'ENERGY']:
                    info['pct_base'] = 'r'  # 非生命和能量属性，m视为r
                elif not info.get('pct_base'):
                    info['pct_base'] = 'r'  # 默认百分比基于当前值
                info['pct_base_desc'] = {
                    'b': '基础',
                    'm': '最大',
                    'r': '当前',
                    'c': '当前'
                }.get(info.get('pct_base'), '当前')
                # 括号标签（可选）
                info['paren'] = ATTRS.get(info.get('paren'), info.get('attr'))
                if highlight_num:
                    res += f"({info['val']}%){info['pct_base_desc']}{info['paren']}"
                else:
                    res += f"{info['val']}%{info['pct_base_desc']}{info['paren']}"
            else:
                if highlight_num:
                    res += f"({info['val']})"
                else:
                    res += f"{info['val']}"
            return res
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

def parse_mode(effect_type: str, mode: str) -> str:
    """
    解析效果目标模式，返回自然语言描述
    :return: 目标描述字符串
    """
    match effect_type:
        case "modify_attr":
            res = ''
            if '_' in mode:
                prefix, suffix = mode.split('_', 1)
                if prefix.startswith('highest') or prefix.startswith('lowest'):
                    attr_code = prefix[len('highest'):] if prefix.startswith('highest') else prefix[len('lowest'):]
                    attr_desc = ATTRS.get(attr_code, attr_code)
                    order_desc = "最高" if prefix.startswith('highest') else "最低"
                    res += f"{attr_desc}{order_desc}的"
                else:
                    prefix_map = {
                        "all": "所有",
                        "random": "随机",
                        "other": "其他"
                    }
                    if prefix not in prefix_map:
                        raise ParseError(f"模式解析失败: 未知前缀 {prefix}")
                    res += f"{prefix_map.get(prefix, '未知目标')}"
                
                if ':' not in suffix and prefix != "all":
                    suffix += ':1'
                if prefix != "all":
                    target_type, count = suffix.split(':', 1)
                    count += "名"
                else:
                    target_type = suffix
                    count = ''
                if prefix == "all" and count:
                    raise ParseError("模式解析失败: 'all' 不能指定数量")
                if target_type in ['ally', 'enemy']:
                    if prefix == "other" and target_type == "enemy":
                        raise ParseError("模式解析失败: 'other' 不能与 'enemy' 组合")
                    target_map = {
                        "ally": "己方角色",
                        "enemy": "敌方角色",
                    }
                    res += f"{count}{target_map.get(target_type, '未知目标')}"
                else:
                    raise ParseError(f"模式解析失败: 未知目标类型 {target_type}")

            else:
                target_map = {
                    "self": "自身",
                    "target": "攻击目标的",
                    "source": "效果来源的",
                    "player": "玩家",
                }
                return target_map.get(mode, "未知目标")
            return res
        case _:
            return "未知目标"

if __name__ == "__main__":
    # effect_str = '{"type": "modify_attr", "param": "MHP+10", "mode": "all_ally"}'
    # effect_dict = json.loads(effect_str)
    # desc = effect_parser(effect_dict)
    # print(desc)

    effects = [{
        "type": "modify_attr",
        "param": "HTE+20%r",
        "mode": "highestHTE_ally"
    },{
        "type": "modify_attr",
        "param": "ATK+10",
        "mode": "self"
    },{
        "type": "modify_attr",
        "param": "HP-15%c",
        "mode": "random_enemy:2"
    },{
        "type": "modify_attr",
        "param": "NRG=30",
        "mode": "player"
    }]
    for effect in effects:
        print(effect)
        info = effect_parser(effect)
        print(info)