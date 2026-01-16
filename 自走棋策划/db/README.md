# 数据库管理系统 📊

> 武林戏自走棋策划的数据库操作完整指南

本系统为自走棋策划提供了一个基于 SQLite 的完整数据管理解决方案，支持角色、羁绊、关键字等游戏数据的可视化编辑和版本控制。

---

## 📁 目录结构

```
自走棋策划/db/
├── new_database.db          # SQLite 数据库文件（.gitignore）
├── dao.py                   # 数据访问层（DAO）
├── service.py               # 业务逻辑层（Service）
├── controller.py            # 控制器层（Controller）
├── character_ui.py          # 角色管理界面
├── fetter_ui.py             # 羁绊管理界面
├── event_ui.py              # 事件管理界面
├── keywords_ui.py           # 关键字管理界面
├── editor_launcher.py       # 编辑器启动器
├── start_ui.py              # 快速启动脚本
├── init_database.py         # 数据库初始化脚本
├── mapper.json              # 数据库字段映射配置
├── error.py                 # 错误定义
└── sql/                     # SQL 版本控制目录
    └── database_dump_new.sql  # 新版数据库快照（Git 追踪）
```

---

## 🏗️ 系统架构

本系统采用经典的三层架构设计：

```
┌─────────────────────────────────────┐
│         UI Layer (界面层)            │
│   character_ui.py, fetter_ui.py    │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│     Controller Layer (控制器层)      │
│         controller.py               │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│      Service Layer (业务逻辑层)      │
│          service.py                 │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│       DAO Layer (数据访问层)         │
│            dao.py                   │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│      Database (SQLite 数据库)       │
│       new_database.db               │
└─────────────────────────────────────┘
```

**职责分离：**
- **UI Layer** - 用户交互和界面展示
- **Controller** - 协调 UI 和 Service
- **Service** - 业务逻辑处理和数据转换
- **DAO** - 数据库 CRUD 操作
- **Database** - 数据持久化存储

---

## 🚀 快速开始

### 启动数据库管理界面

```bash
cd 自走棋策划/db
python start_ui.py
```

启动后会自动：
1. 从 `sql/database_dump_new.sql` 同步最新数据
2. 打开可视化管理界面
3. 关闭时自动保存更改到 SQL 文件

### 界面功能

启动后可以看到多个标签页：

- **角色管理** - 查看、添加、编辑、删除角色
- **羁绊管理** - 管理角色羁绊关系
- **关键字管理** - 管理游戏关键字
- **事件管理** - 管理游戏事件

---

## 📊 数据库结构（新版）

### Character 表 - 角色表

存储所有角色的基础属性和战斗数据。

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | - | 角色唯一标识 |
| `name` | TEXT | NOT NULL | - | 角色名称 |
| `attack_power` | INTEGER | - | 4 | 攻击力 |
| `health_points` | INTEGER | - | 8 | 生命值 |
| `speed` | INTEGER | - | 2 | 速度 |
| `hate_value` | INTEGER | - | 1 | 仇恨值 |
| `price` | INTEGER | - | 1 | 购买价格 |
| `weapon` | TEXT | - | '[]' | 武器列表（JSON 数组） |
| `energy` | INTEGER | - | 0 | 初始能量 |
| `avaliable_location` | TEXT | - | '[]' | 可站位置（JSON 数组） |
| `hate_matrix` | TEXT | - | '[[1,1,1],[1,1,1],[1,1,1]]' | 仇恨矩阵（JSON） |
| `max_initiative` | INTEGER | - | 10 | 最大先攻值 |

**示例数据：**
```sql
INSERT INTO Character VALUES(
    1, 
    '测试角色1', 
    4, 8, 2, 1, 2, 
    NULL, 
    0, 
    NULL, 
    NULL, 
    10
);
```

### Fetter 表 - 羁绊表

定义羁绊效果和触发条件。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | TEXT | PRIMARY KEY (复合) | 羁绊唯一标识 |
| `numofpeople` | INTEGER | PRIMARY KEY (复合) | 触发人数要求 |
| `description` | TEXT | - | 羁绊效果描述 |

**主键说明：** `(id, numofpeople)` 复合主键，同一羁绊可以有多个人数档位。

**示例数据：**
```sql
INSERT INTO Fetter VALUES('武当', 3, '略');
INSERT INTO Fetter VALUES('武当', 5, '略');
INSERT INTO Fetter VALUES('少林', 3, '略');
INSERT INTO Fetter VALUES('炁体源流', 3, '最大能量增加3');
```

### CharacterFetter 表 - 角色羁绊关联表

管理角色与羁绊的多对多关系。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `character_id` | INTEGER | PRIMARY KEY (复合), NOT NULL | 角色 ID |
| `fetter_id` | TEXT | PRIMARY KEY (复合), NOT NULL | 羁绊 ID |

**示例数据：**
```sql
INSERT INTO CharacterFetter VALUES(1, '武当');
INSERT INTO CharacterFetter VALUES(2, '武当');
INSERT INTO CharacterFetter VALUES(2, '峨眉');
```

---

## 🔧 DAO 层使用指南

### 连接数据库

```python
from dao import connect_database

conn = connect_database()  # 连接到 new_database.db
# 使用连接进行查询...
conn.close()
```

### CharacterDao - 角色数据访问

```python
from dao import CharacterDao, connect_database

dao = CharacterDao()
conn = connect_database()

# 查询所有角色
all_chars = dao.select_all_characters(conn)
print(all_chars)

# 根据 ID 查询
char = dao.select_character_by_id(1, conn)
print(char)

# 根据价格查询
chars_price_2 = dao.select_character_by_price(2, conn)

# 插入新角色
# 注意：values 是列表，对应 mapper 中的字段顺序
values = [None, '新角色', 5, 10, 3, 1, 2, '[]', 0, '[]', '[[1,1,1],[1,1,1],[1,1,1]]', 10]
new_id = dao.insert_character(values, conn)
print(f"新角色 ID: {new_id}")

# 更新角色
update_values = ['更新后的名字', 6, 12, 3, 1, 2, '[]', 0, '[]', '[[1,1,1],[1,1,1],[1,1,1]]', 10]
dao.update_character(new_id, update_values, conn)

# 删除角色
dao.delete_character(new_id, conn)

conn.commit()
conn.close()
```

### FetterDao - 羁绊数据访问

```python
from dao import FetterDao, connect_database

fdao = FetterDao()
conn = connect_database()

# 查询所有羁绊
all_fetters = fdao.select_all_fetters(conn)

# 根据羁绊名查询
wudang_fetters = fdao.select_fetter_by_id('武当', conn)

# 插入新羁绊
values = ['华山', 3, '增加剑法伤害']
fdao.insert_fetter(values, conn)

# 更新羁绊
update_values = ['增加剑法伤害20%']
fdao.update_fetter(('华山', 3), update_values, conn)

# 删除羁绊
fdao.delete_fetter(('华山', 3), conn)

conn.commit()
conn.close()
```

### CharacterFetterDao - 角色羁绊关联

```python
from dao import CharacterFetterDao, connect_database

cfdao = CharacterFetterDao()
conn = connect_database()

# 为角色添加羁绊
cfdao.insert_character_fetter([1, '武当'], conn)

# 查询角色的所有羁绊
fetters = cfdao.get_fetters_by_char_id(1, conn)
print(fetters)

# 删除角色的羁绊
cfdao.delete_character_fetter((1, '武当'), conn)

conn.commit()
conn.close()
```

---

## 🎯 Service 层使用指南

Service 层封装了业务逻辑，提供更高级的操作。

### CharacterService - 角色业务逻辑

```python
from service import CharacterService

service = CharacterService()

# 获取所有角色（自动解析 JSON 字段和羁绊）
all_chars = service.select_all_characters()
for char in all_chars:
    print(f"{char['name']}: {char['fetters']}")

# 插入新角色（自动处理羁绊关联）
new_char = {
    'name': '张三丰',
    'attack_power': 8,
    'health_points': 15,
    'speed': 4,
    'price': 5,
    'fetters': ['武当', '炁体源流']  # 自动关联羁绊
}
service.insert_character(new_char)

# 更新角色
service.update_character(1, {'attack_power': 10})

# 删除角色
service.delete_character(1)
```

### FetterService - 羁绊业务逻辑

```python
from service import FetterService

fservice = FetterService()

# 获取所有羁绊
fetters = fservice.get_all_fetters()

# 插入新羁绊
new_fetter = {
    'id': '华山',
    'numofpeople': 3,
    'description': '增加剑法伤害20%'
}
fservice.insert_fetter(new_fetter)

# 更新羁绊
fservice.update_fetter(('华山', 3), {'description': '增加剑法伤害30%'})
```

---

## 🎨 Controller 层使用指南

Controller 层提供界面友好的接口。

```python
from controller import CharacterControl

ctrl = CharacterControl()

# 获取所有角色
chars = ctrl.get_all_characters()

# 获取下一个可用 ID
next_id = ctrl.get_next_character_id()

# 添加角色
new_char = {
    'name': '新角色',
    'fetters': ['武当']
}
success = ctrl.add_character(new_char)

# 更新角色
ctrl.update_character(1, {'attack_power': 12})

# 删除角色
ctrl.delete_character(1)

# 导出 JSON
ctrl.dumpJson()
```

---

## 🔄 数据库版本控制

### Git 集成策略

为了实现团队协作和版本追踪：

1. **`.db` 文件不提交** - 数据库文件在 `.gitignore` 中
2. **SQL 文件追踪** - 通过 `sql/database_dump_new.sql` 追踪数据变更
3. **自动同步** - UI 启动/关闭时自动导入/导出

### 版本控制函数

#### updateDb() - 从 SQL 恢复数据库

```python
from dao import updateDb

# 从 sql/database_dump_new.sql 重建数据库
updateDb()
```

**何时使用：**
- 拉取最新代码后
- 数据库文件损坏时
- 需要回滚到 Git 版本时

#### dumpSql() - 导出数据库为 SQL

```python
from dao import dumpSql

# 导出数据库到 sql/database_dump_new.sql
dumpSql()
```

**何时使用：**
- 完成数据编辑后
- 提交代码前
- 创建数据快照时

### 团队协作工作流

```bash
# 1. 拉取最新代码
git pull

# 2. 启动 UI（自动执行 updateDb）
cd 自走棋策划/db
python start_ui.py

# 3. 进行数据编辑...

# 4. 关闭 UI（自动执行 dumpSql）

# 5. 提交变更
git add sql/database_dump_new.sql
git commit -m "更新角色数据"
git push
```

---

## 📝 Mapper 配置系统

`mapper.json` 定义了数据库结构和 SQL 语句模板。

### Mapper 结构

```json
{
  "CharacterDao": {
    "fields": {
      "id": {
        "type": "INTEGER",
        "primary_key": true,
        "autoincrement": true
      },
      "name": {
        "type": "TEXT",
        "not_null": true
      },
      "attack_power": {
        "type": "INTEGER",
        "default": 4
      }
      // ...更多字段
    },
    "create_table_query": "CREATE TABLE IF NOT EXISTS ...",
    "insert_query": "INSERT INTO Character ...",
    "update_query": "UPDATE Character SET ..."
  }
}
```

### 动态添加字段

```python
from dao import CharacterDao

dao = CharacterDao()

# 添加新字段到 mapper
new_field = {
    "type": "INTEGER",
    "default": 0,
    "not_null": False
}
dao.insert_column_to_mapper('new_field_name', new_field)

# 在数据库中添加列
dao.insert_column('new_field_name', 'INTEGER', default_value=0)
```

---

## 🛠️ 高级操作

### 导出 JSON 配置文件

将数据库数据导出为游戏配置文件：

```python
from service import dumpJson

# 导出到 ../py灰盒/character_config.json
dumpJson()
```

### 初始化数据库

首次使用时从 JSON 导入数据：

```bash
cd 自走棋策划/db
python init_database.py
```

### 创建/删除表

```python
from dao import create_table, drop_table

# 创建表
create_table('Character')

# 删除表
drop_table('Character')
```

---

## ⚠️ 注意事项

1. **事务管理** - 所有修改操作后需要调用 `conn.commit()`
2. **连接关闭** - 使用完连接后务必 `conn.close()`
3. **JSON 字段** - `weapon`, `avaliable_location`, `hate_matrix` 存储为 JSON 字符串
4. **主键约束** - Fetter 和 CharacterFetter 使用复合主键
5. **外键约束** - CharacterFetter 的 character_id 应对应 Character 的 id
6. **版本控制** - 只关注 `database_dump_new.sql`，忽略旧版 SQL 文件

---

## 📚 依赖项

所有依赖均为 Python 标准库，无需额外安装：

- `sqlite3` - 数据库操作
- `json` - JSON 处理
- `tkinter` - GUI 界面
- `pathlib` - 路径处理
- `uuid6` - UUID 生成（需 pip 安装：`pip install uuid6`）

---

## 🐛 常见问题

### Q: 数据库文件找不到？

A: 系统会自动创建 `new_database.db`，如果丢失可运行 `updateDb()` 恢复。

### Q: SQL 文件冲突如何解决？

A: 保留远程版本，重新启动 UI 会自动同步最新数据。

### Q: 如何批量导入角色？

A: 编辑 JSON 配置文件后运行 `init_database.py`。

### Q: UI 关闭后数据丢失？

A: 检查是否正常关闭 UI（触发 dumpSql），否则手动调用 `dumpSql()`。

---

## 📖 相关文档

- [根目录 README](../../README.md) - 项目总体介绍
- [TODO.md](../../TODO.md) - 待开发功能
- [功能模块总结.md](../../功能模块总结.md) - 模块详解

---

**更新日期**: 2026-01-16  
**数据库版本**: New (database_dump_new.sql)  
**维护者**: xs-www/wulin_drama 团队
