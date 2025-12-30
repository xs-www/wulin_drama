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

_term_console = Console() 

class Entry:
    import datetime

    def __init__(self, content: str, info_type: str = "INFO", timestamp: str = None):
        self.content = content
        self.timestamp = timestamp if timestamp is not None else self.datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
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
        import os, datetime
        if file_path is None:
            file_path = f"logs/game_log_{datetime.datetime.now().strftime('%Y-%m-%d')}.txt"

        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        with open(file_path, 'a', encoding='utf-8') as file:
            for entry in self.entries:
                file.write(str(entry) + "\n")
        self.clearLog()

log = Log()
    
class Damage:

    pass

def load_json_config(file_path: str) -> dict:
    import json
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def load_character_config(char_id: int) -> dict:
    config = load_json_config('character_config.json')
    return config.get(str(char_id), EMPTY_CHARACTER_CONFIG)

def matrix_multiply(matA: list, matB: list) -> list:
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

if __name__ == "__main__":
    # Test matrix multiplication
    matA = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    matB = [[9, 8, 7], [6, 5, 4], [3, 2, 1]]
    multiplied = matrix_multiply(matA, matB)
    print("Matrix Multiplication Result:", multiplied)