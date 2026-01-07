#!/usr/bin/env python3
"""
快速启动 Character 数据库管理 UI
"""
import sys, os
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from editor_launcher import main

if __name__ == '__main__':
    print("正在启动 Character 数据库管理界面...")
    print("提示：")
    print("  - 启动时会自动从 SQL 文件同步数据库")
    print("  - 关闭时会自动保存更改到 SQL 文件")
    print("  - 所有数据通过 Git 追踪 sql/database_dump.sql 文件")
    print()
    main()
