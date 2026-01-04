# 内容管理系统使用指南

## 概述

内容管理系统允许您查看、编辑和管理已生成的游戏内容，包括：
- 战斗日志
- 角色配置
- 战斗状态

## 功能特性

### ✅ 已实现功能

1. **日志管理**
   - 列出所有日志文件
   - 查看日志内容（支持限制行数）
   - 按类型或关键词过滤日志
   - 修改日志文件（删除行、替换文本）
   - 自动备份原文件

2. **角色配置管理**
   - 列出所有角色
   - 查看角色详细配置
   - 修改角色属性（攻击力、生命值、速度等）
   - 添加新角色
   - 删除角色
   - 批量修改角色
   - 自动备份原配置

3. **战斗状态管理**
   - 保存战斗状态到文件
   - 列出所有保存的战斗
   - 查看战斗详情
   - 修改战斗状态
   - 删除战斗记录

## 安装

所有功能已集成到项目中，无需额外安装。

## 使用方法

### 命令行工具

使用 `content_editor.py` 命令行工具进行内容管理：

```bash
cd 自走棋策划/py灰盒
python content_editor.py [命令] [子命令] [参数]
```

### 日志管理示例

#### 列出所有日志文件
```bash
python content_editor.py logs list
```

#### 查看日志内容
```bash
# 查看完整日志
python content_editor.py logs view game_log_2025-12-30.txt

# 只显示前20行
python content_editor.py logs view game_log_2025-12-30.txt --limit 20

# 按关键词过滤
python content_editor.py logs view game_log_2025-12-30.txt --keyword "defeated"

# 按类型过滤
python content_editor.py logs view game_log_2025-12-30.txt --filter-type "ERROR"
```

#### 修改日志文件
```bash
# 删除包含特定关键词的行
python content_editor.py logs modify game_log_2025-12-30.txt delete_lines --keyword "Round 1"

# 替换文本
python content_editor.py logs modify game_log_2025-12-30.txt replace --old-text "Ch1" --new-text "Hero1"
```

### 角色管理示例

#### 列出所有角色
```bash
python content_editor.py character list
```

#### 查看角色详情
```bash
python content_editor.py character view 0002
```

#### 修改角色属性
```bash
# 修改攻击力和生命值
python content_editor.py character modify 0002 --attack 15 --health 50

# 修改名称
python content_editor.py character modify 0002 --name "强力战士"

# 修改速度
python content_editor.py character modify 0002 --speed 10
```

#### 添加新角色
```bash
python content_editor.py character add 0011 --name "新角色" --attack 20 --health 100 --speed 8
```

#### 删除角色
```bash
# 需要确认
python content_editor.py character delete 0011

# 跳过确认
python content_editor.py character delete 0011 --confirm
```

### 战斗状态管理示例

#### 列出所有战斗状态
```bash
python content_editor.py battle list
```

#### 查看战斗详情
```bash
python content_editor.py battle view battle_test_20260104_100000.json
```

### Python API 使用

您也可以在 Python 代码中直接使用内容管理器：

```python
from content_manager import LogReader, CharacterConfigManager, BattleStateManager

# 日志管理
log_reader = LogReader()
log_files = log_reader.list_log_files()
logs = log_reader.filter_logs("game_log_2025-12-30.txt", keyword="defeated")

# 角色管理
char_manager = CharacterConfigManager()
char_manager.modify_character("0002", {"attack_power": 20, "health_points": 100})

# 战斗状态管理
battle_manager = BattleStateManager()
battle_data = {"round": 1, "winner": "red"}
battle_manager.save_battle_state("test_battle", battle_data)
```

### 在模拟器中保存战斗状态

修改 `main.py` 以启用战斗状态保存：

```python
from simulator import attackSimulator

# 启用战斗状态保存
battle_history = attackSimulator(game_board, save_state=True, battle_id="my_battle")
```

## 备份机制

所有修改操作都会自动创建备份文件：

- **角色配置备份**：`character_config.backup_YYYYMMDD_HHMMSS.json`
- **日志备份**：`game_log_YYYY-MM-DD.txt.backup_YYYYMMDD_HHMMSS`
- **战斗状态备份**：`battle_*.backup_YYYYMMDD_HHMMSS.json`

删除操作也会重命名为 `.deleted_*` 而不是真正删除。

## 高级功能

### 批量修改角色

```python
from content_manager import CharacterConfigManager

manager = CharacterConfigManager()
modifications = {
    "0002": {"attack_power": 15},
    "0003": {"attack_power": 18},
    "0004": {"attack_power": 25}
}
count = manager.batch_modify(modifications)
print(f"修改了 {count} 个角色")
```

### 日志过滤

```python
from content_manager import LogReader

reader = LogReader()
# 过滤特定时间段的日志
filtered = reader.filter_logs(
    "game_log_2025-12-30.txt",
    start_time="2025/12/30-21:00:00",
    end_time="2025/12/30-22:00:00"
)
```

## 文件结构

```
自走棋策划/py灰盒/
├── content_manager.py      # 内容管理器核心模块
├── content_editor.py       # 命令行工具
├── simulator.py           # 战斗模拟器（已增强）
├── character_config.json  # 角色配置文件
├── logs/                  # 日志目录
│   └── game_log_*.txt
└── battle_states/         # 战斗状态保存目录
    └── battle_*.json
```

## 常见问题

### Q: 修改角色后游戏崩溃？
A: 检查修改的属性值是否合理。建议先在备份上测试。

### Q: 如何恢复备份？
A: 找到相应的 `.backup_*` 文件，重命名并去掉 `.backup_*` 后缀。

### Q: 可以同时修改多个日志文件吗？
A: 可以，使用 Python API 编写脚本进行批量操作。

### Q: 战斗状态文件太大怎么办？
A: 可以在模拟器中设置 `save_state=False` 禁用保存功能。

## 最佳实践

1. **定期清理备份文件**：备份文件会占用磁盘空间
2. **测试修改**：在正式使用前先测试修改效果
3. **版本控制**：将重要的配置文件纳入 Git 版本控制
4. **文档记录**：记录重要的修改操作

## 贡献

欢迎提交问题和改进建议到项目仓库。

## 许可证

与主项目相同。
