EMPTY_CHARACTER_CONFIG = {
    "id": "000",
    "name": "Example Character",
    "attack_power": 4,
    "health_points": 8,
    "avaliable_location": [],
    "speed": 2,
    "fetter": [],
    "hate_value": 1,
    "price": 1,
    "hate_matrix": [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ]
}

from rich.console import Console
import uuid, os
from datetime import datetime

_term_console = Console()

from pathlib import Path

# 当前正在执行的 .py 文件绝对目录
BASE_DIR = Path(__file__).resolve().parent

def timestampDate():
    """
    获取当前时间戳，格式为 "YYYY/MM/DD"。
    :return: 当前时间戳字符串
    """
    return datetime.now().strftime("%Y-%m-%d")

def timestampTime():
    """
    获取当前时间戳，格式为 "YYYY/MM/DD-HH:MM:SS"。
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

class Log:
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
            self.clearLog()
        return True
    
    def getLog(self) -> list:
        return self.entries
    
    # 追加日志到文件尾
    def saveLog(self, file_path: str = None):
        if file_path is None:
            file_path = f"{BASE_DIR}/logs/game_log_{timestampDate()}.txt"

        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        with open(file_path, 'a', encoding='utf-8') as file:
            for entry in self.entries:
                file.write(str(entry) + "\n")
        self.clearLog()

log = Log()

# @todo
class Damage:

    pass

# @todo
class Skill:

    pass

class Buff:

    def __init__(self, inflicator, bearer, name: str, duration: int, effect: dict):
        
        self.inflicator = inflicator
        self.bearer = bearer

        self.name = name
        self.duration = duration  # 回合数
        self.effect = effect      # 效果描述
        self.buff_id = uuid.uuid4()

    def isActive(self) -> bool:
        return self.duration > 0
    
    def update(self):
        if self.duration > 0:
            self.duration -= 1

class Effect:

    def __init__(self, name: str, effect_type: str, value: float):
        self.name = name
        self.effect_type = effect_type
        self.value = value

def loadJsonConfig(file_path: str) -> dict:
    import json
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def loadCharacterAttrs(char_id: str) -> dict:
    config = loadJsonConfig(BASE_DIR / 'character_config.json')
    return config.get(char_id, EMPTY_CHARACTER_CONFIG)

def matrixMultiply(matA: list, matB: list) -> list:
    result = []
    for i in range(len(matA)):
        result_row = []
        for j in range(len(matA[0])):
            result_row.append(matA[i][j] * matB[i][j])
        result.append(result_row)
    return result

def roll(dice_sides: int) -> int:
    import random
    return random.randint(1, dice_sides)


class EventManager:
    def __init__(self):
        # 事件监听器字典，结构：{事件名: [回调函数1, 回调函数2, ...]}
        self.listeners = {}

        log.console("EventManager initialized.", "INFO")

    def register(self, event_name: str, callback):
        """
        注册事件监听器。
        :param event_name: 事件名称（字符串）
        :param callback:   回调函数，函数签名需匹配事件参数
        """
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(callback)

        log.console(f"Registered event '{event_name}' with callback {callback.__name__}.", "INFO")

    def unregister(self, event_name: str, callback):
        """
        注销事件监听器。
        :param event_name: 事件名称
        :param callback:   需移除的回调函数
        """
        if event_name in self.listeners:
            self.listeners[event_name].remove(callback)

    def broadcast(self, event_name: str, **context):
        """
        广播（触发）事件，将 context 作为参数传递给所有监听器。
        :param event_name: 事件名称
        :param context:    任意关键字参数
        """
        log.console(f"{event_name} triggered with context {context}", "EVENT")

        if event_name in self.listeners:
            for callback in self.listeners[event_name]:
                callback(**context)

class Signal():
    def __init__(self):
        self._slots = []

    def connect(self, slot):
        self._slots.append(slot)

    def disconnect(self, slot):
        if slot in self._slots:
            self._slots.remove(slot)

    def emit(self, *args, **kwargs):
        for slot in self._slots:
            slot(*args, **kwargs)

event_manager = EventManager()

if __name__ == "__main__":
    b = Buff('a', 'b', "Test Buff", 3, {"attack_power": +2})
    print(b.name, b.duration, b.effect, b.buff_id)