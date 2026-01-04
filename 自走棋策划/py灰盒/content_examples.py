#!/usr/bin/env python3
"""
内容管理示例 - 演示如何使用内容管理系统
Content Management Examples - Demonstrates how to use the content management system
"""

from content_manager import LogReader, BattleStateManager, CharacterConfigManager
from util import log

def example1_view_logs():
    """示例1: 查看战斗日志"""
    print("\n" + "=" * 60)
    print("示例 1: 查看战斗日志")
    print("=" * 60)
    
    reader = LogReader()
    
    # 列出所有日志文件
    log_files = reader.list_log_files()
    print(f"\n可用的日志文件 ({len(log_files)} 个):")
    for f in log_files:
        print(f"  - {f}")
    
    if log_files:
        # 查看第一个日志文件中被击败的记录
        print(f"\n查看 {log_files[0]} 中的击败记录:")
        defeated_logs = reader.filter_logs(log_files[0], keyword="defeated")
        for entry in defeated_logs[:5]:  # 只显示前5条
            print(f"  [{entry['timestamp']}] {entry['content']}")

def example2_modify_character():
    """示例2: 修改角色属性"""
    print("\n" + "=" * 60)
    print("示例 2: 修改角色属性")
    print("=" * 60)
    
    manager = CharacterConfigManager()
    
    # 查看原始属性
    char_id = "0002"
    original = manager.get_character(char_id)
    print(f"\n角色 {char_id} 原始属性:")
    print(f"  名称: {original.get('name')}")
    print(f"  攻击力: {original.get('attack_power')}")
    print(f"  生命值: {original.get('health_points')}")
    
    # 修改属性（这里只是演示，实际不会保存）
    print(f"\n如果要修改攻击力为 20:")
    print(f"  manager.modify_character('{char_id}', {{'attack_power': 20}})")
    print(f"  或使用 CLI: python content_editor.py character modify {char_id} --attack 20")

def example3_save_battle_state():
    """示例3: 保存战斗状态"""
    print("\n" + "=" * 60)
    print("示例 3: 保存战斗状态")
    print("=" * 60)
    
    manager = BattleStateManager()
    
    # 创建示例战斗数据
    battle_data = {
        "round": 5,
        "red_team": [
            {"name": "勇士", "hp": 50, "atk": 15, "position": ("front", 1)},
            {"name": "法师", "hp": 30, "atk": 25, "position": ("back", 2)}
        ],
        "blue_team": [
            {"name": "骑士", "hp": 80, "atk": 10, "position": ("front", 2)},
            {"name": "弓箭手", "hp": 40, "atk": 20, "position": ("back", 1)}
        ],
        "status": "ongoing"
    }
    
    print("\n保存战斗状态示例:")
    print(f"  回合: {battle_data['round']}")
    print(f"  红队: {len(battle_data['red_team'])} 个角色")
    print(f"  蓝队: {len(battle_data['blue_team'])} 个角色")
    
    # 保存
    filepath = manager.save_battle_state("example_battle", battle_data)
    print(f"\n✓ 战斗状态已保存到: {filepath}")
    
    # 读取验证 - 使用保存返回的完整路径
    import os
    filename = os.path.basename(filepath)
    loaded = manager.load_battle_state(filename)
    print(f"✓ 验证: 成功加载回合 {loaded.get('round')} 的战斗状态")

def example4_batch_modify():
    """示例4: 批量修改角色"""
    print("\n" + "=" * 60)
    print("示例 4: 批量修改角色（演示）")
    print("=" * 60)
    
    print("\n批量修改多个角色的攻击力示例:")
    print("```python")
    print("manager = CharacterConfigManager()")
    print("modifications = {")
    print("    '0002': {'attack_power': 15},")
    print("    '0003': {'attack_power': 18},")
    print("    '0004': {'attack_power': 25}")
    print("}")
    print("count = manager.batch_modify(modifications)")
    print("print(f'修改了 {count} 个角色')")
    print("```")

def example5_log_filtering():
    """示例5: 高级日志过滤"""
    print("\n" + "=" * 60)
    print("示例 5: 高级日志过滤")
    print("=" * 60)
    
    reader = LogReader()
    log_files = reader.list_log_files()
    
    if log_files:
        filename = log_files[0]
        
        # 按类型过滤
        print(f"\n在 {filename} 中查找不同类型的日志:")
        
        for log_type in ["INFO"]:
            filtered = reader.filter_logs(filename, log_type=log_type)
            print(f"  {log_type}: {len(filtered)} 条")
        
        # 按关键词过滤
        keywords = ["Round", "defeated", "counterattack"]
        print(f"\n按关键词过滤:")
        for keyword in keywords:
            filtered = reader.filter_logs(filename, keyword=keyword)
            print(f"  包含 '{keyword}': {len(filtered)} 条")

def main():
    """运行所有示例"""
    print("\n" + "=" * 70)
    print(" 内容管理系统使用示例")
    print(" Content Management System Examples")
    print("=" * 70)
    
    try:
        example1_view_logs()
        example2_modify_character()
        example3_save_battle_state()
        example4_batch_modify()
        example5_log_filtering()
        
        print("\n" + "=" * 70)
        print(" 所有示例运行完成！")
        print(" 更多信息请查看: CONTENT_MANAGEMENT_GUIDE.md")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ 运行示例时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
