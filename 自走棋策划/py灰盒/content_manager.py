"""
内容管理器 - 用于管理和修改已生成的游戏内容
Content Manager - For managing and modifying generated game content
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from util import BASE_DIR, timestampTime, log


class LogReader:
    """日志读取和管理器 - Log Reader and Manager"""
    
    def __init__(self, log_dir: str = None):
        """
        初始化日志读取器
        :param log_dir: 日志目录路径，默认为 BASE_DIR/logs
        """
        self.log_dir = Path(log_dir) if log_dir else BASE_DIR / "logs"
        if not self.log_dir.exists():
            self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def list_log_files(self) -> List[str]:
        """列出所有日志文件"""
        if not self.log_dir.exists():
            return []
        return sorted([f.name for f in self.log_dir.glob("game_log_*.txt")])
    
    def read_log_file(self, filename: str) -> List[str]:
        """
        读取指定日志文件的所有行
        :param filename: 日志文件名
        :return: 日志行列表
        """
        filepath = self.log_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"日志文件不存在: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.readlines()
    
    def parse_log_entry(self, line: str) -> Optional[Dict[str, str]]:
        """
        解析单条日志
        :param line: 日志行
        :return: 解析后的字典 {timestamp, type, content} 或 None
        """
        line = line.strip()
        if not line:
            return None
        
        # 格式: [YYYY/MM/DD-HH:MM:SS] [TYPE] content
        try:
            parts = line.split("] ", 2)
            if len(parts) >= 3:
                timestamp = parts[0][1:]  # 去掉开头的 [
                log_type = parts[1][1:]    # 去掉开头的 [
                content = parts[2]
                return {
                    "timestamp": timestamp,
                    "type": log_type,
                    "content": content
                }
        except Exception:
            pass
        
        return {"timestamp": "", "type": "RAW", "content": line}
    
    def filter_logs(self, filename: str, 
                   log_type: str = None, 
                   keyword: str = None,
                   start_time: str = None,
                   end_time: str = None) -> List[Dict[str, str]]:
        """
        过滤日志内容
        :param filename: 日志文件名
        :param log_type: 日志类型过滤 (INFO, WARN, ERROR, etc.)
        :param keyword: 关键词过滤
        :param start_time: 起始时间
        :param end_time: 结束时间
        :return: 过滤后的日志列表
        """
        lines = self.read_log_file(filename)
        filtered = []
        
        for line in lines:
            entry = self.parse_log_entry(line)
            if not entry:
                continue
            
            # 应用过滤条件
            if log_type and entry.get("type") != log_type:
                continue
            if keyword and keyword not in entry.get("content", ""):
                continue
            if start_time and entry.get("timestamp", "") < start_time:
                continue
            if end_time and entry.get("timestamp", "") > end_time:
                continue
            
            filtered.append(entry)
        
        return filtered
    
    def modify_log_file(self, filename: str, new_lines: List[str], backup: bool = True):
        """
        修改日志文件内容
        :param filename: 日志文件名
        :param new_lines: 新的日志内容行列表
        :param backup: 是否创建备份
        """
        filepath = self.log_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"日志文件不存在: {filepath}")
        
        # 创建备份
        if backup:
            backup_path = self.log_dir / f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(filepath, 'r', encoding='utf-8') as src:
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
        
        # 写入新内容
        with open(filepath, 'w', encoding='utf-8') as f:
            for line in new_lines:
                f.write(line if line.endswith('\n') else line + '\n')
    
    def delete_log_file(self, filename: str, backup: bool = True):
        """
        删除日志文件
        :param filename: 日志文件名
        :param backup: 是否先备份
        """
        filepath = self.log_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"日志文件不存在: {filepath}")
        
        if backup:
            backup_path = self.log_dir / f"{filename}.deleted_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(filepath, backup_path)
        else:
            os.remove(filepath)


class BattleStateManager:
    """战斗状态管理器 - Battle State Manager"""
    
    def __init__(self, save_dir: str = None):
        """
        初始化战斗状态管理器
        :param save_dir: 保存目录，默认为 BASE_DIR/battle_states
        """
        self.save_dir = Path(save_dir) if save_dir else BASE_DIR / "battle_states"
        if not self.save_dir.exists():
            self.save_dir.mkdir(parents=True, exist_ok=True)
    
    def save_battle_state(self, battle_id: str, battle_data: Dict[str, Any]) -> str:
        """
        保存战斗状态
        :param battle_id: 战斗ID
        :param battle_data: 战斗数据字典
        :return: 保存的文件路径
        """
        filename = f"battle_{battle_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.save_dir / filename
        
        # 添加元数据
        battle_data["metadata"] = {
            "battle_id": battle_id,
            "saved_at": timestampTime(),
            "version": "1.0"
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(battle_data, f, ensure_ascii=False, indent=2)
        
        return str(filepath)
    
    def load_battle_state(self, filename: str) -> Dict[str, Any]:
        """
        加载战斗状态
        :param filename: 文件名或完整路径
        :return: 战斗数据字典
        """
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        
        filepath = Path(filename)
        if not filepath.is_absolute():
            filepath = self.save_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"战斗状态文件不存在: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_battle_states(self) -> List[str]:
        """列出所有保存的战斗状态文件"""
        if not self.save_dir.exists():
            return []
        return sorted([f.name for f in self.save_dir.glob("battle_*.json")])
    
    def modify_battle_state(self, filename: str, modifications: Dict[str, Any], backup: bool = True) -> str:
        """
        修改战斗状态
        :param filename: 文件名
        :param modifications: 要修改的内容字典
        :param backup: 是否创建备份
        :return: 修改后的文件路径
        """
        battle_data = self.load_battle_state(filename)
        
        # 创建备份
        if backup:
            backup_filename = filename.replace('.json', f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            backup_path = self.save_dir / backup_filename
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(battle_data, f, ensure_ascii=False, indent=2)
        
        # 应用修改
        def deep_update(base_dict: dict, update_dict: dict):
            """递归更新字典"""
            for key, value in update_dict.items():
                if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                    deep_update(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        deep_update(battle_data, modifications)
        
        # 更新修改时间
        if "metadata" not in battle_data:
            battle_data["metadata"] = {}
        battle_data["metadata"]["modified_at"] = timestampTime()
        
        # 保存修改
        filepath = self.save_dir / filename if not Path(filename).is_absolute() else Path(filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(battle_data, f, ensure_ascii=False, indent=2)
        
        return str(filepath)
    
    def delete_battle_state(self, filename: str, backup: bool = True):
        """
        删除战斗状态文件
        :param filename: 文件名
        :param backup: 是否先备份
        """
        filepath = self.save_dir / filename if not Path(filename).is_absolute() else Path(filename)
        if not filepath.exists():
            raise FileNotFoundError(f"战斗状态文件不存在: {filepath}")
        
        if backup:
            backup_path = self.save_dir / f"{filename}.deleted_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(filepath, backup_path)
        else:
            os.remove(filepath)


class CharacterConfigManager:
    """角色配置管理器 - Character Configuration Manager"""
    
    def __init__(self, config_file: str = None):
        """
        初始化角色配置管理器
        :param config_file: 配置文件路径，默认为 BASE_DIR/character_config.json
        """
        self.config_file = Path(config_file) if config_file else BASE_DIR / "character_config.json"
        self.config_data = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_file.exists():
            return {}
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_config(self, backup: bool = True):
        """保存配置文件"""
        if backup and self.config_file.exists():
            backup_path = self.config_file.parent / f"{self.config_file.stem}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(self.config_file, 'r', encoding='utf-8') as src:
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config_data, f, ensure_ascii=False, indent=2)
    
    def get_character(self, char_id: str) -> Optional[Dict[str, Any]]:
        """获取角色配置"""
        return self.config_data.get(char_id)
    
    def list_characters(self) -> List[str]:
        """列出所有角色ID"""
        return list(self.config_data.keys())
    
    def modify_character(self, char_id: str, modifications: Dict[str, Any], backup: bool = True) -> bool:
        """
        修改角色配置
        :param char_id: 角色ID
        :param modifications: 要修改的属性字典
        :param backup: 是否创建备份
        :return: 是否成功
        """
        if char_id not in self.config_data:
            log.console(f"角色ID不存在: {char_id}", "WARN")
            return False
        
        # 应用修改
        for key, value in modifications.items():
            self.config_data[char_id][key] = value
        
        self._save_config(backup=backup)
        log.console(f"角色 {char_id} 配置已修改", "OK")
        return True
    
    def add_character(self, char_id: str, char_data: Dict[str, Any], backup: bool = True) -> bool:
        """
        添加新角色
        :param char_id: 角色ID
        :param char_data: 角色数据
        :param backup: 是否创建备份
        :return: 是否成功
        """
        if char_id in self.config_data:
            log.console(f"角色ID已存在: {char_id}", "WARN")
            return False
        
        char_data["id"] = char_id
        self.config_data[char_id] = char_data
        self._save_config(backup=backup)
        log.console(f"已添加角色 {char_id}", "OK")
        return True
    
    def delete_character(self, char_id: str, backup: bool = True) -> bool:
        """
        删除角色
        :param char_id: 角色ID
        :param backup: 是否创建备份
        :return: 是否成功
        """
        if char_id not in self.config_data:
            log.console(f"角色ID不存在: {char_id}", "WARN")
            return False
        
        del self.config_data[char_id]
        self._save_config(backup=backup)
        log.console(f"已删除角色 {char_id}", "OK")
        return True
    
    def batch_modify(self, modifications: Dict[str, Dict[str, Any]], backup: bool = True) -> int:
        """
        批量修改角色配置
        :param modifications: {char_id: {attr: value, ...}, ...}
        :param backup: 是否创建备份
        :return: 成功修改的角色数量
        """
        count = 0
        for char_id, mods in modifications.items():
            if char_id in self.config_data:
                for key, value in mods.items():
                    self.config_data[char_id][key] = value
                count += 1
        
        if count > 0:
            self._save_config(backup=backup)
            log.console(f"批量修改了 {count} 个角色的配置", "OK")
        
        return count


# 导出主要类
__all__ = ['LogReader', 'BattleStateManager', 'CharacterConfigManager']


if __name__ == "__main__":
    # 测试代码
    print("内容管理器模块加载成功")
    
    # 测试日志读取器
    log_reader = LogReader()
    log_files = log_reader.list_log_files()
    print(f"找到 {len(log_files)} 个日志文件")
    
    # 测试角色配置管理器
    char_manager = CharacterConfigManager()
    characters = char_manager.list_characters()
    print(f"找到 {len(characters)} 个角色配置")
