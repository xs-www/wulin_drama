from rich.console import Console
import uuid, os
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