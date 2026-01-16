
ERROR_DICT = {
    "DataValueError": {"code": 3001, "message": "数据值错误"},
}

class DataValueError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)