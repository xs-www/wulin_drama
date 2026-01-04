#!/usr/bin/env python3
"""
测试内容管理系统功能
Test script for content management system
"""

import sys
from content_manager import LogReader, BattleStateManager, CharacterConfigManager

def test_log_reader():
    """测试日志读取器"""
    print("=" * 60)
    print("测试日志读取器 (Testing Log Reader)")
    print("=" * 60)
    
    reader = LogReader()
    
    # 列出日志文件
    log_files = reader.list_log_files()
    print(f"\n✓ 找到 {len(log_files)} 个日志文件")
    
    if log_files:
        # 读取第一个日志文件
        first_log = log_files[0]
        print(f"✓ 读取日志: {first_log}")
        
        # 过滤日志
        filtered = reader.filter_logs(first_log, keyword="defeated")
        print(f"✓ 找到 {len(filtered)} 条包含 'defeated' 的日志")
        
        if filtered:
            print(f"  示例: {filtered[0]['content'][:50]}...")
    
    print("\n日志读取器测试完成 ✓\n")

def test_character_manager():
    """测试角色配置管理器"""
    print("=" * 60)
    print("测试角色配置管理器 (Testing Character Manager)")
    print("=" * 60)
    
    manager = CharacterConfigManager()
    
    # 列出角色
    chars = manager.list_characters()
    print(f"\n✓ 找到 {len(chars)} 个角色配置")
    
    # 查看一个角色
    if chars:
        first_char = chars[0]
        char_data = manager.get_character(first_char)
        print(f"✓ 角色 {first_char}: {char_data.get('name', 'Unknown')}")
        if char_data and len(char_data) > 1:
            print(f"  攻击力: {char_data.get('attack_power', '?')}")
            print(f"  生命值: {char_data.get('health_points', '?')}")
    
    print("\n角色配置管理器测试完成 ✓\n")

def test_battle_manager():
    """测试战斗状态管理器"""
    print("=" * 60)
    print("测试战斗状态管理器 (Testing Battle Manager)")
    print("=" * 60)
    
    manager = BattleStateManager()
    
    # 创建测试战斗状态
    test_battle = {
        "round": 1,
        "red_team": [
            {"name": "TestChar1", "hp": 100, "atk": 10}
        ],
        "blue_team": [
            {"name": "TestChar2", "hp": 80, "atk": 15}
        ]
    }
    
    print("\n✓ 创建测试战斗状态")
    filepath = manager.save_battle_state("test", test_battle)
    print(f"✓ 保存到: {filepath}")
    
    # 列出战斗状态
    battles = manager.list_battle_states()
    print(f"✓ 找到 {len(battles)} 个战斗状态文件")
    
    # 读取刚保存的战斗
    if battles:
        loaded = manager.load_battle_state(battles[-1])
        print(f"✓ 成功加载战斗状态")
        print(f"  回合数: {loaded.get('round', 'N/A')}")
    
    print("\n战斗状态管理器测试完成 ✓\n")

def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始测试内容管理系统")
    print("=" * 60 + "\n")
    
    try:
        test_log_reader()
        test_character_manager()
        test_battle_manager()
        
        print("=" * 60)
        print("所有测试完成 ✅")
        print("=" * 60 + "\n")
        
        return 0
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
