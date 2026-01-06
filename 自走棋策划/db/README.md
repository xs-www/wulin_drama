# Character 数据库管理系统

本系统为自走棋策划提供了一个基于 SQLite 的 Character 数据管理解决方案，包含数据访问层和可视化界面。

## 目录结构

```
自走棋策划/db/
├── database.db           # SQLite 数据库文件（.gitignore）
├── dao.py               # 数据访问层
├── ui.py                # 可视化管理界面
├── init_database.py     # 数据库初始化脚本
└── sql/                 # SQL 版本控制目录
    └── database_dump.sql  # 数据库导出文件（用于 Git 追踪）
```

## 功能特性

### dao.py - 数据访问层

#### 核心函数

1. **connect_database(db_path=None)**
   - 连接到 SQLite 数据库
   - 返回数据库连接对象

2. **CharacterDao 类**
   - `create(character_dict)`: 创建新角色（传入字典）
   - `read(character_id)`: 根据 ID 读取角色
   - `read_all()`: 读取所有角色
   - `update(character_id, character_dict)`: 更新角色（传入 ID 和字典）
   - `delete(character_id)`: 删除角色（传入 ID）

3. **dumpJson(output_path=None, db_path=None)**
   - 将 character 表导出为 JSON 文件
   - 默认导出到 `../py灰盒/character_config.json`

4. **updateDb(db_path=None)**
   - 清空 database.db 并根据 sql 文件夹内的 .sql 文件重构整个数据库
   - 用于从 Git 同步数据库版本

5. **dumpSql(db_path=None, output_dir=None)**
   - 导出数据库为 .sql 文件到 sql 文件夹
   - 用于 Git 版本追踪

### ui.py - 可视化界面

使用 tkinter 构建的图形界面，提供以下功能：

#### 主要功能

1. **Character 列表视图**
   - 显示所有 Character 的基本信息（ID、名称、攻击力、生命值、速度）
   - 支持选择查看详细信息

2. **详情视图**
   - 以 JSON 格式显示选中 Character 的完整信息

3. **操作按钮**
   - **新建**: 打开对话框创建新 Character
   - **编辑**: 编辑选中的 Character
   - **删除**: 删除选中的 Character
   - **刷新**: 重新加载列表
   - **导出 JSON**: 导出数据到 character_config.json

4. **自动版本管理**
   - 启动时自动执行 `updateDb()` 从 SQL 文件同步数据库
   - 关闭时自动执行 `dumpSql()` 保存更改到 SQL 文件

## 使用方法

### 启动 UI

```bash
cd 自走棋策划/db
python3 ui.py
```

### 使用 DAO 进行编程操作

```python
from dao import CharacterDao, dumpJson, updateDb, dumpSql

# 创建 DAO 实例
dao = CharacterDao()

# 创建角色
new_char = {
    'id': '0011',
    'name': 'new_character',
    'attack_power': 10,
    'health_points': 100,
    'speed': 5,
    'hate_value': 2,
    'price': 3,
    'avaliable_location': ['front', 'middle'],
    'hate_matrix': [[1, 1, 1], [1, 2, 1], [1, 1, 1]]
}
dao.create(new_char)

# 读取角色
char = dao.read('0011')
print(char)

# 更新角色
dao.update('0011', {'attack_power': 15})

# 删除角色
dao.delete('0011')

# 导出 JSON
dumpJson()

# 从 SQL 重建数据库
updateDb()

# 导出 SQL
dumpSql()
```

## 数据库结构

### character 表

| 字段名 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| id | TEXT | 主键，角色 ID | - |
| name | TEXT | 角色名称（必填） | - |
| localization | TEXT | 本地化名称 | NULL |
| attack_power | INTEGER | 攻击力 | 4 |
| health_points | INTEGER | 生命值 | 8 |
| speed | INTEGER | 速度 | 2 |
| hate_value | INTEGER | 仇恨值 | 1 |
| price | INTEGER | 价格 | 1 |
| weapon | TEXT | 武器 | NULL |
| energy | INTEGER | 能量 | 0 |
| avaliable_location | TEXT | 可用位置（JSON） | NULL |
| fetter | TEXT | 羁绊（JSON） | NULL |
| hate_matrix | TEXT | 仇恨矩阵（JSON） | NULL |

## 版本控制策略

- `.db` 文件已加入 `.gitignore`，不会提交到 Git
- 数据库版本通过 `sql/database_dump.sql` 文件进行追踪
- 团队成员通过以下流程同步数据：
  1. 拉取最新代码后，启动 UI（会自动执行 `updateDb()`）
  2. 进行数据修改
  3. 关闭 UI（会自动执行 `dumpSql()`）
  4. 提交 `sql/database_dump.sql` 的变更

## 依赖

- Python 3.x
- sqlite3（Python 标准库）
- tkinter（Python 标准库）
- json（Python 标准库）

所有依赖都是 Python 内置库，无需额外安装。

## 初始化

首次使用时，可以运行初始化脚本从现有的 `character_config.json` 导入数据：

```bash
cd 自走棋策划/db
python3 init_database.py
```

这将创建数据库并导入现有的角色数据。
