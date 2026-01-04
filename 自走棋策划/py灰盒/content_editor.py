#!/usr/bin/env python3
"""
内容编辑器 - 命令行工具用于管理和修改已生成的内容
Content Editor - CLI tool for managing and modifying generated content
"""

import sys
import argparse
from content_manager import LogReader, BattleStateManager, CharacterConfigManager
from util import log


class ContentEditor:
    """内容编辑器主类"""
    
    def __init__(self):
        self.log_reader = LogReader()
        self.battle_manager = BattleStateManager()
        self.char_manager = CharacterConfigManager()
    
    def list_logs(self, args):
        """列出所有日志文件"""
        log_files = self.log_reader.list_log_files()
        
        if not log_files:
            print("没有找到日志文件")
            return
        
        print(f"\n找到 {len(log_files)} 个日志文件:")
        for i, filename in enumerate(log_files, 1):
            print(f"  {i}. {filename}")
        print()
    
    def view_log(self, args):
        """查看日志内容"""
        filename = args.filename
        
        try:
            if args.filter_type or args.keyword:
                # 使用过滤器
                entries = self.log_reader.filter_logs(
                    filename,
                    log_type=args.filter_type,
                    keyword=args.keyword
                )
                
                if not entries:
                    print("没有匹配的日志条目")
                    return
                
                print(f"\n匹配的日志条目 ({len(entries)} 条):")
                for entry in entries[:args.limit] if args.limit else entries:
                    print(f"[{entry['timestamp']}] [{entry['type']}] {entry['content']}")
            else:
                # 查看完整日志
                lines = self.log_reader.read_log_file(filename)
                display_lines = lines[:args.limit] if args.limit else lines
                
                print(f"\n日志文件: {filename} (共 {len(lines)} 行)")
                if args.limit and len(lines) > args.limit:
                    print(f"显示前 {args.limit} 行:\n")
                
                for line in display_lines:
                    print(line.rstrip())
        
        except FileNotFoundError as e:
            print(f"错误: {e}")
        except Exception as e:
            print(f"读取日志时出错: {e}")
    
    def modify_log(self, args):
        """修改日志文件"""
        filename = args.filename
        
        try:
            # 读取现有内容
            lines = self.log_reader.read_log_file(filename)
            print(f"当前日志有 {len(lines)} 行")
            
            if args.action == "delete_lines":
                # 删除包含特定关键词的行
                keyword = args.keyword
                new_lines = [line for line in lines if keyword not in line]
                print(f"删除了 {len(lines) - len(new_lines)} 行包含 '{keyword}' 的内容")
                
            elif args.action == "replace":
                # 替换文本
                old_text = args.old_text
                new_text = args.new_text
                new_lines = [line.replace(old_text, new_text) for line in lines]
                count = sum(1 for old, new in zip(lines, new_lines) if old != new)
                print(f"在 {count} 行中替换了文本")
            
            else:
                print("不支持的操作")
                return
            
            # 保存修改
            self.log_reader.modify_log_file(filename, new_lines, backup=True)
            print(f"日志文件已修改，原文件已备份")
        
        except FileNotFoundError as e:
            print(f"错误: {e}")
        except Exception as e:
            print(f"修改日志时出错: {e}")
    
    def list_characters(self, args):
        """列出所有角色"""
        char_ids = self.char_manager.list_characters()
        
        if not char_ids:
            print("没有找到角色配置")
            return
        
        print(f"\n找到 {len(char_ids)} 个角色:")
        for char_id in char_ids:
            char_data = self.char_manager.get_character(char_id)
            name = char_data.get('name', 'Unknown') if char_data else 'Unknown'
            if char_data and len(char_data) > 1:  # 有实际数据
                atk = char_data.get('attack_power', '?')
                hp = char_data.get('health_points', '?')
                print(f"  {char_id}: {name} (攻击:{atk}, 生命:{hp})")
            else:
                print(f"  {char_id}: (空配置)")
        print()
    
    def view_character(self, args):
        """查看角色详细信息"""
        char_id = args.char_id
        char_data = self.char_manager.get_character(char_id)
        
        if not char_data:
            print(f"角色 {char_id} 不存在")
            return
        
        print(f"\n角色 {char_id} 的配置:")
        import json
        print(json.dumps(char_data, ensure_ascii=False, indent=2))
        print()
    
    def modify_character(self, args):
        """修改角色属性"""
        char_id = args.char_id
        
        if not self.char_manager.get_character(char_id):
            print(f"角色 {char_id} 不存在")
            return
        
        modifications = {}
        
        # 解析修改参数
        if args.name:
            modifications['name'] = args.name
        if args.attack is not None:
            modifications['attack_power'] = args.attack
        if args.health is not None:
            modifications['health_points'] = args.health
        if args.speed is not None:
            modifications['speed'] = args.speed
        
        if not modifications:
            print("没有指定要修改的属性")
            return
        
        # 应用修改
        success = self.char_manager.modify_character(char_id, modifications, backup=True)
        
        if success:
            print(f"角色 {char_id} 已修改:")
            for key, value in modifications.items():
                print(f"  {key}: {value}")
            print("原配置文件已备份")
    
    def add_character(self, args):
        """添加新角色"""
        char_id = args.char_id
        
        char_data = {
            "id": char_id,
            "name": args.name or f"Character_{char_id}",
            "attack_power": args.attack or 5,
            "health_points": args.health or 100,
            "speed": args.speed or 5,
            "hate_value": 1,
            "price": 1
        }
        
        success = self.char_manager.add_character(char_id, char_data, backup=True)
        
        if success:
            print(f"已添加角色 {char_id}")
            import json
            print(json.dumps(char_data, ensure_ascii=False, indent=2))
    
    def delete_character(self, args):
        """删除角色"""
        char_id = args.char_id
        
        if not args.confirm:
            confirm = input(f"确认删除角色 {char_id}? (y/n): ")
            if confirm.lower() != 'y':
                print("已取消")
                return
        
        success = self.char_manager.delete_character(char_id, backup=True)
        
        if success:
            print(f"已删除角色 {char_id}，原配置文件已备份")
    
    def list_battles(self, args):
        """列出所有保存的战斗状态"""
        battle_files = self.battle_manager.list_battle_states()
        
        if not battle_files:
            print("没有找到保存的战斗状态")
            return
        
        print(f"\n找到 {len(battle_files)} 个战斗状态文件:")
        for i, filename in enumerate(battle_files, 1):
            print(f"  {i}. {filename}")
        print()
    
    def view_battle(self, args):
        """查看战斗状态详情"""
        filename = args.filename
        
        try:
            battle_data = self.battle_manager.load_battle_state(filename)
            
            print(f"\n战斗状态: {filename}")
            import json
            print(json.dumps(battle_data, ensure_ascii=False, indent=2))
            print()
        
        except FileNotFoundError as e:
            print(f"错误: {e}")
        except Exception as e:
            print(f"读取战斗状态时出错: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="武林戏内容编辑器 - 管理和修改已生成的游戏内容",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 日志相关命令
    log_parser = subparsers.add_parser('logs', help='日志管理')
    log_subparsers = log_parser.add_subparsers(dest='log_command')
    
    # 列出日志
    list_logs_parser = log_subparsers.add_parser('list', help='列出所有日志文件')
    list_logs_parser.set_defaults(func='list_logs')
    
    # 查看日志
    view_log_parser = log_subparsers.add_parser('view', help='查看日志内容')
    view_log_parser.add_argument('filename', help='日志文件名')
    view_log_parser.add_argument('--limit', type=int, help='限制显示行数')
    view_log_parser.add_argument('--filter-type', help='按类型过滤 (INFO, WARN, ERROR)')
    view_log_parser.add_argument('--keyword', help='按关键词过滤')
    view_log_parser.set_defaults(func='view_log')
    
    # 修改日志
    modify_log_parser = log_subparsers.add_parser('modify', help='修改日志文件')
    modify_log_parser.add_argument('filename', help='日志文件名')
    modify_log_parser.add_argument('action', choices=['delete_lines', 'replace'], help='操作类型')
    modify_log_parser.add_argument('--keyword', help='删除包含此关键词的行')
    modify_log_parser.add_argument('--old-text', help='要替换的文本')
    modify_log_parser.add_argument('--new-text', help='替换为的文本')
    modify_log_parser.set_defaults(func='modify_log')
    
    # 角色相关命令
    char_parser = subparsers.add_parser('character', help='角色管理')
    char_subparsers = char_parser.add_subparsers(dest='char_command')
    
    # 列出角色
    list_chars_parser = char_subparsers.add_parser('list', help='列出所有角色')
    list_chars_parser.set_defaults(func='list_characters')
    
    # 查看角色
    view_char_parser = char_subparsers.add_parser('view', help='查看角色详情')
    view_char_parser.add_argument('char_id', help='角色ID')
    view_char_parser.set_defaults(func='view_character')
    
    # 修改角色
    modify_char_parser = char_subparsers.add_parser('modify', help='修改角色属性')
    modify_char_parser.add_argument('char_id', help='角色ID')
    modify_char_parser.add_argument('--name', help='角色名称')
    modify_char_parser.add_argument('--attack', type=int, help='攻击力')
    modify_char_parser.add_argument('--health', type=int, help='生命值')
    modify_char_parser.add_argument('--speed', type=int, help='速度')
    modify_char_parser.set_defaults(func='modify_character')
    
    # 添加角色
    add_char_parser = char_subparsers.add_parser('add', help='添加新角色')
    add_char_parser.add_argument('char_id', help='角色ID')
    add_char_parser.add_argument('--name', help='角色名称')
    add_char_parser.add_argument('--attack', type=int, help='攻击力')
    add_char_parser.add_argument('--health', type=int, help='生命值')
    add_char_parser.add_argument('--speed', type=int, help='速度')
    add_char_parser.set_defaults(func='add_character')
    
    # 删除角色
    delete_char_parser = char_subparsers.add_parser('delete', help='删除角色')
    delete_char_parser.add_argument('char_id', help='角色ID')
    delete_char_parser.add_argument('--confirm', action='store_true', help='跳过确认')
    delete_char_parser.set_defaults(func='delete_character')
    
    # 战斗状态相关命令
    battle_parser = subparsers.add_parser('battle', help='战斗状态管理')
    battle_subparsers = battle_parser.add_subparsers(dest='battle_command')
    
    # 列出战斗
    list_battles_parser = battle_subparsers.add_parser('list', help='列出所有战斗状态')
    list_battles_parser.set_defaults(func='list_battles')
    
    # 查看战斗
    view_battle_parser = battle_subparsers.add_parser('view', help='查看战斗状态')
    view_battle_parser.add_argument('filename', help='战斗状态文件名')
    view_battle_parser.set_defaults(func='view_battle')
    
    # 解析参数
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 执行命令
    editor = ContentEditor()
    
    if hasattr(args, 'func'):
        func = getattr(editor, args.func)
        func(args)
    else:
        print("请指定具体的子命令")
        if args.command == 'logs':
            log_parser.print_help()
        elif args.command == 'character':
            char_parser.print_help()
        elif args.command == 'battle':
            battle_parser.print_help()


if __name__ == "__main__":
    main()
