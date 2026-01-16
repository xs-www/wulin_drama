# wulin_drama (武林戏) 🎮

> 武林主题的回合制自走棋游戏开发与武侠故事创作综合项目

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)

## 📖 项目简介

武林戏是一个以中国武侠文化为主题的游戏开发项目，包含两大核心模块：

1. **自走棋战斗模拟器** - 基于网格的回合制自走棋战斗系统
2. **武侠故事文档管理** - 完整的武侠世界观和角色传记管理

项目采用数据驱动设计，支持通过配置文件和数据库快速定义角色、技能和羁绊，适合用于原型开发、玩法验证和内容创作。

---

## ✨ 核心特性

### 🎯 自走棋战斗系统

- **🔢 基于网格的战斗** - 3x3 网格布局，前排/中排/后排定位系统
- **🎲 智能目标选择** - 基于仇恨值矩阵的动态目标系统
- **⚔️ 攻击与反击** - 自动战斗模拟，支持攻击和反击机制
- **💥 多样化伤害系统** - 支持物理伤害、魔法伤害等多种伤害类型
- **🔗 羁绊系统** - 角色间的羁绊关系，提供组队策略深度
- **📊 实时战斗日志** - 完整的战斗过程记录和美化输出

### 💾 数据库管理系统

- **📝 可视化编辑器** - 基于 Tkinter 的图形化角色/羁绊管理界面
- **🗃️ SQLite 数据库** - 结构化数据存储，支持复杂查询
- **🔄 版本控制集成** - 自动 SQL 导出/导入，Git 友好的数据管理
- **🏗️ 三层架构** - DAO/Service/Controller 分层设计
- **🔌 灵活的数据映射** - 通过 mapper.json 配置数据库结构

### 🎨 事件驱动架构

- **📡 事件管理器** - 装饰器风格的事件订阅 (@em.on())
- **🔧 高可扩展性** - 轻松添加新技能、效果和游戏机制
- **🎯 解耦设计** - 战斗逻辑与数据分离，便于维护

---

## 🚀 快速开始

### 环境要求

- Python 3.x
- SQLite3（Python 标准库自带）
- 依赖包：`pygame`, `rich`, `uuid6`

### 安装依赖

```bash
pip install pygame rich uuid6
```

### 运行战斗模拟器

```bash
cd 自走棋策划/py灰盒
python main.py
```

### 启动数据库管理界面

```bash
cd 自走棋策划/db
python start_ui.py
```

启动后可以：
- 查看和编辑所有角色数据
- 管理角色羁绊关系
- 添加或删除角色
- 导出数据到 JSON 配置文件

---

## 📁 项目结构

```
wulin_drama/
├── 自走棋策划/                    # 自走棋游戏开发主目录
│   ├── db/                       # 数据库管理系统
│   │   ├── new_database.db       # SQLite 数据库文件（git ignore）
│   │   ├── dao.py                # 数据访问层
│   │   ├── service.py            # 业务逻辑层
│   │   ├── controller.py         # 控制器层
│   │   ├── character_ui.py       # 角色管理界面
│   │   ├── fetter_ui.py          # 羁绊管理界面
│   │   ├── start_ui.py           # UI 启动脚本
│   │   ├── mapper.json           # 数据库字段映射配置
│   │   └── sql/                  # SQL 版本控制目录
│   │       └── database_dump_new.sql  # 数据库快照（Git 追踪）
│   ├── py灰盒/                   # Python 战斗模拟器
│   │   ├── main.py               # 主程序入口
│   │   ├── game.py               # 游戏主循环
│   │   ├── entity.py             # 实体和角色类
│   │   ├── character.py          # 角色定义
│   │   ├── grid.py               # 网格系统
│   │   ├── simulator.py          # 战斗模拟器
│   │   ├── effect.py             # 效果系统
│   │   ├── keywords.py           # 关键字系统
│   │   ├── util.py               # 工具函数（Buff、Damage等）
│   │   ├── character_config.json # 角色配置文件
│   │   ├── windows/              # UI 窗口模块
│   │   └── logs/                 # 战斗日志目录
│   ├── godot_demo/               # Godot 引擎原型
│   └── 文档规范/                  # 游戏设计文档
├── mjyl/                         # 武侠故事文档
│   ├── *.docx                    # 角色传记文档
│   └── 时间线.xlsm               # 时间线管理表格
├── README.md                     # 本文件
├── TODO.md                       # 待办事项
└── 功能模块总结.md                # 功能模块文档
```

---

## 🎮 核心模块说明

### 1️⃣ 数据库管理系统 (db/)

完整的数据管理解决方案，支持角色、羁绊、关键字等游戏数据的可视化编辑。

**核心特性：**
- 三层架构设计（DAO/Service/Controller）
- 支持复杂的关联查询（角色-羁绊多对多关系）
- 自动版本控制（启动时从 SQL 导入，关闭时导出）
- 支持动态添加/删除数据库字段

**主要表结构：**
- `Character` - 角色表（攻击力、生命值、速度等）
- `Fetter` - 羁绊表（羁绊 ID、人数要求、效果描述）
- `CharacterFetter` - 角色羁绊关联表

📚 详细文档请查看：[db/README.md](自走棋策划/db/README.md)

### 2️⃣ 战斗模拟器 (py灰盒/)

基于事件驱动的回合制战斗系统，支持复杂的战斗机制。

**核心类：**
- `Character` - 角色实体（属性、技能、Buff 管理）
- `GameBoard` - 游戏棋盘（红蓝双方，角色布局）
- `GameGrid` - 战斗网格（3x3 网格，位置管理）
- `BattleSimulator` - 战斗模拟器（战斗流程控制）
- `EventManager` - 事件管理器（事件发布/订阅）

**已实现系统：**
- ✅ 角色属性系统
- ✅ 网格定位系统
- ✅ 目标选择系统（仇恨矩阵）
- ✅ 伤害计算系统
- ✅ 攻击/反击机制
- ✅ Buff 框架
- ✅ 事件管理系统
- ✅ 日志系统

**开发中系统：**
- ⏳ 技能系统（Skill class）
- ⏳ 装备系统（Equipment class）
- ⏳ 回合管理器（RoundManager）
- ⏳ 关键字效果系统

### 3️⃣ 武侠故事文档 (mjyl/)

武侠世界观设定和角色传记管理。

**包含内容：**
- 完整的角色传记（剑主系列、才子传等）
- 时间线管理表格
- 角色关系图谱

---

## 🔧 使用指南

### 创建新角色

#### 方法 1：使用数据库管理界面（推荐）

```bash
cd 自走棋策划/db
python start_ui.py
```

在界面中点击"新建"按钮，填写角色信息即可。

#### 方法 2：直接编辑配置文件

编辑 `自走棋策划/py灰盒/character_config.json`：

```json
{
  "0001": {
    "id": "0001",
    "name": "测试角色",
    "attack_power": 10,
    "health_points": 100,
    "speed": 5,
    "hate_value": 2,
    "price": 3,
    "weapon": ["sword"],
    "energy": 0,
    "avaliable_location": ["front", "middle"],
    "hate_matrix": [[2,1,1],[1,2,1],[1,1,2]]
  }
}
```

### 管理羁绊关系

在数据库管理界面中：
1. 切换到"羁绊管理"标签
2. 添加新羁绊或编辑现有羁绊
3. 在角色编辑界面中为角色分配羁绊

### 导出数据

数据库管理系统支持导出为 JSON 格式供战斗模拟器使用：

```bash
cd 自走棋策划/db
python -c "from dao import dumpJson; dumpJson()"
```

或在 UI 界面中点击"导出 JSON"按钮。

---

## 🛠️ 技术栈

| 技术 | 用途 |
|------|------|
| Python 3.x | 主要开发语言 |
| SQLite | 数据存储 |
| Tkinter | GUI 界面 |
| Pygame | 游戏渲染和精灵管理 |
| Rich | 终端美化输出 |
| JSON | 配置文件格式 |

---

## 📋 开发路线图

### 已完成 ✅
- [x] 基础战斗模拟器
- [x] 角色系统
- [x] 网格系统  
- [x] 事件管理器
- [x] 数据库管理系统
- [x] 可视化编辑器
- [x] 羁绊系统基础

### 进行中 🚧
- [ ] 技能系统（Skill class）
- [ ] 回合管理器（RoundManager）
- [ ] 关键字效果系统

### 计划中 📝
- [ ] 装备系统
- [ ] 完整的 UI 界面（Pygame）
- [ ] 更多角色和技能
- [ ] 羁绊系统完善
- [ ] AI 决策系统

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

在开发前请先：
1. 阅读 [TODO.md](TODO.md) 了解待开发功能
2. 阅读 [功能模块总结.md](功能模块总结.md) 了解项目架构

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 📮 联系方式

- 项目仓库：[xs-www/wulin_drama](https://github.com/xs-www/wulin_drama)
- Issue 反馈：[GitHub Issues](https://github.com/xs-www/wulin_drama/issues)

---

**Happy Coding! 🎉 武林有你更精彩！**