# 武林戏 (wulin_drama) - TODO 功能模块整理

本文档整理了项目中所有待实现和待完善的功能模块。

## 📋 总体开发路线（来自 README.md）

### 已完成 ✅
- [x] 基础战斗模拟器
- [x] 角色系统
- [x] 网格系统
- [x] 事件管理器

### 待开发 📝
- [ ] UI 界面开发
- [ ] 更多角色和技能
- [ ] 羁绊系统完善
- [ ] 装备系统

---

## 🎯 代码中的 TODO 清单

### 1. 角色属性更新系统 (entity.py)

**位置**: `自走棋策划/py灰盒/entity.py:81-83`

```python
# @todo
def updateInGameAttrs(self):
    pass
```

**功能描述**:
- 更新角色在战斗中的属性
- 需要根据装备、Buff、羁绊等因素动态计算角色属性

**优先级**: 🔴 高
- 装备系统和羁绊系统的实现依赖此功能
- 影响角色战斗力的动态计算

**相关模块**:
- 装备系统 (Equipment class)
- Buff 系统 (Buff class in util.py)
- 羁绊系统 (fetter system)

**实现建议**:
1. 计算装备提供的属性加成
2. 计算激活的羁绊效果
3. 应用所有激活的 Buff 效果
4. 更新 in_game_attrs 字典中的各项数值

---

### 2. 装备系统 (entity.py)

**位置**: `自走棋策划/py灰盒/entity.py:167-171`

```python
# @todo
class Equipment:
    def __init__(self):
        pass
```

**功能描述**:
- 实现完整的装备系统
- 包括武器、护甲、饰品三个装备槽

**优先级**: 🟠 中
- 已在 README 开发路线中列出
- Character 类已预留 equipments 字典

**需要实现的内容**:
1. **装备基础属性**:
   - 装备ID
   - 装备名称
   - 装备类型（weapon/armor/accessory）
   - 属性加成（攻击力、生命值等）
   - 稀有度/品质
   - 价格

2. **装备效果系统**:
   - 被动效果
   - 主动技能
   - 触发条件

3. **装备管理**:
   - 装备穿戴/卸下
   - 装备约束检查（武器类型限制等）
   - 装备效果应用

**相关文件**:
- `entity.py` - Equipment 类定义
- `character.py` - 角色装备管理
- `character_config.json` - 装备配置数据

---

### 3. 回合管理器 (simulator.py)

**位置**: `自走棋策划/py灰盒/simulator.py:84-91`

```python
# @todo
class RoundManager:
    def __init__(self):
        self.current_round = 1

    def nextRound(self):
        self.current_round += 1
```

**功能描述**:
- 完善回合管理系统
- 处理回合开始/结束时的各种事件

**优先级**: 🟠 中
- 当前战斗系统可以运行，但缺少回合管理
- Buff 系统的持续时间需要回合管理

**需要实现的内容**:
1. **回合生命周期管理**:
   - 回合开始事件触发
   - 回合结束事件触发
   - 回合计数和时间管理

2. **回合相关功能**:
   - Buff 持续时间更新
   - 回合制技能冷却
   - 能量恢复机制
   - DoT（持续伤害）效果处理

3. **事件广播**:
   - 利用现有的 EventManager (em) 广播回合事件
   - before_round_start
   - after_round_start
   - before_round_end
   - after_round_end

**相关模块**:
- Buff 系统（需要回合计数更新持续时间）
- 技能系统（技能冷却）
- 能量系统（能量恢复）

---

### 4. 技能系统 (util.py)

**位置**: `自走棋策划/py灰盒/util.py:99-102`

```python
# @todo
class Skill:
    pass
```

**功能描述**:
- 实现完整的技能系统
- 包括主动技能和被动技能

**优先级**: 🔴 高
- README 中"更多角色和技能"依赖此功能
- 当前战斗系统只有普通攻击

**需要实现的内容**:
1. **技能基础属性**:
   - 技能ID和名称
   - 技能类型（主动/被动）
   - 技能描述
   - 冷却时间
   - 能量消耗
   - 目标类型（单体/群体/自身等）

2. **技能效果系统**:
   - 伤害技能（物理/魔法）
   - 治疗技能
   - Buff/Debuff 施加
   - 位移技能
   - 控制技能（眩晕、沉默等）

3. **技能触发机制**:
   - 手动触发（能量满时）
   - 被动触发（战斗开始、受击、击杀等）
   - 条件触发（生命值低于阈值等）

4. **技能与事件系统集成**:
   - 利用 EventManager 处理技能触发
   - 技能效果的事件广播

**相关功能**:
- 能量系统（Character 类中已有 energy 属性）
- 伤害系统（已有 Damage 类）
- Buff 系统（已有 Buff 类）

**实现参考**:
```python
class Skill:
    def __init__(self, skill_id: str, name: str, skill_type: str, 
                 cooldown: int, energy_cost: int, effect: dict):
        self.skill_id = skill_id
        self.name = name
        self.skill_type = skill_type  # "active" or "passive"
        self.cooldown = cooldown
        self.energy_cost = energy_cost
        self.effect = effect  # 效果描述
        self.current_cooldown = 0
    
    def canUse(self, character: Character) -> bool:
        # 检查能量和冷却
        pass
    
    def use(self, caster: Character, target: Character):
        # 执行技能效果
        pass
```

---

## 🔗 功能模块依赖关系

```
技能系统 (Skill)
    ├─→ 能量系统 (Character.energy)
    ├─→ Buff系统 (Buff)
    ├─→ 回合管理器 (RoundManager)
    └─→ 事件管理器 (EventManager)

装备系统 (Equipment)
    └─→ 角色属性更新 (updateInGameAttrs)
        └─→ 羁绊系统 (fetter)

回合管理器 (RoundManager)
    ├─→ Buff系统 (Buff持续时间)
    ├─→ 技能系统 (技能冷却)
    └─→ 事件管理器 (回合事件)
```

---

## 📊 开发优先级建议

### 第一阶段（核心战斗）
1. **技能系统** - 让战斗更有趣
2. **角色属性更新系统** - 为装备和羁绊打基础
3. **回合管理器** - 完善战斗流程

### 第二阶段（系统扩展）
4. **装备系统** - 增加策略深度
5. **羁绊系统完善** - 增加队伍搭配策略
6. **更多角色和技能** - 丰富内容

### 第三阶段（用户体验）
7. **UI 界面开发** - 提升用户体验

---

## 📝 补充说明

### 已有的良好基础
项目已经建立了很好的架构基础：
- ✅ 事件管理器 (EventManager) - 支持事件驱动设计
- ✅ Buff 系统框架 (Buff class) - 已定义基本结构
- ✅ 日志系统 (Log class) - 完善的日志记录
- ✅ 伤害系统 (Damage class) - 支持不同伤害类型
- ✅ 网格战斗系统 (GameGrid, GameBoard) - 完整的位置管理
- ✅ 角色数据配置系统 (JSON配置 + CSV转换工具)

### 建议的开发方向
1. 优先实现**技能系统**，让战斗系统更丰富
2. 完善**回合管理**，让 Buff 和技能冷却能正常运作
3. 实现**装备系统**，增加角色的可定制性
4. 最后考虑 **UI 开发**，在核心玩法稳定后提升体验

---

## 🎮 当前可运行的功能

虽然有很多 TODO，但项目当前已经可以运行基础的自走棋战斗模拟：
- ✅ 角色创建和配置（通过 JSON）
- ✅ 战斗网格布局（3x3 前中后排）
- ✅ 自动战斗模拟
- ✅ 基于仇恨值的智能目标选择
- ✅ 攻击和反击机制
- ✅ 战斗日志记录

运行命令：
```bash
cd 自走棋策划/py灰盒
python main.py
```

---

**文档生成时间**: 2026-01-04  
**项目仓库**: xs-www/wulin_drama  
**分支**: copilot/todo
