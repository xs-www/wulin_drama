"""
effect.py - 实现效果(Effect)、增益/减益(Buff)和增益列表(BuffList)的管理系统
"""

from typing import Tuple, List, Dict, Optional
from types import SimpleNamespace
import re

class Condition:

    TYPE = SimpleNamespace(
        ALWAYS="always",
        CONSUNRG="consume_energy",
        CONSUHP="consume_hp",
        HASSTATU="has_statu",
        GOTHURT="got_hurt"
    )
    """
    条件类，表示触发效果的条件
    """
    def __init__(self, condi_type: str, param):
        """
        初始化条件
        :param condition_type: 条件类型 (例如: "on_attack", "on_damage")
        :param parameters: 条件参数字典
        """
        self.condi_type = condi_type
        self.param = param

    def check(self, **context) -> bool:
        """
        检查条件是否满足
        :param context: 上下文参数，用于条件判断
        :return: True表示条件满足，False表示不满足
        """
        match self.condi_type:
            case Condition.TYPE.ALWAYS:
                return True
            case Condition.TYPE.CONSUNRG:
                char = context.get("character", None)
                required_energy = self.param.get("energy", 0)
                return char.getAttr("current.energy") >= required_energy
            case Condition.TYPE.CONSUHP:
                char = context.get("character", None)
                required_hp = self.param.get("hp", 0)
                return char.getAttr("current.hp") >= required_hp
            case Condition.TYPE.HASSTATU:
                char = context.get("character", None)
                statu_name = self.param.get("statu_name", "")
                return char.hasStatus(statu_name)
            case Condition.TYPE.GOTHURT:
                char = context.get("character", None)
                return char.getAttr("current.hp") < char.getAttr("max.hp")
            case _:
                return False
    
    def __str__(self):
        return f"Condition({self.condi_type}, {self.param})"
    
    def __repr__(self):
        return self.__str__()
    
    def byDict(cls, data: dict) -> "Condition":
        """
        通过字典创建Condition实例
        :param data: 包含 type 和 param 的字典
        :return: Condition实例
        """
        return cls(
            condi_type=data.get("type", ""),
            param=data.get("param", {})
        )
    
ALWAYS_CONDITION = Condition(Condition.TYPE.ALWAYS, None)
    
class Effect:
    """
    
    """
    ATTRS = {
        "ATK": "atk",
        "MHP": "max_hp",
        "HP": "hp",
        "DMG": "damage",
        "SPD": "speed",
        "SPEED": "speed",
        "NRG": "energy",
        "ENERGY": "energy",
        "HATE": "hate_value",
        "CRTRA": "critical_rate",
        "CRTDMG": "critical_damage"
    }

    def __init__(self, effect_type: str, param: str, mode: str):
        """
        初始化效果
        """
        self.effect_type = effect_type
        self.param = param
        self.mode = mode
    
    def parse(self):
        """
        解析效果参数字符串，返回结构化信息
        :return: 解析后的信息字典
        """
        match self.effect_type:
            case "modify_attr":
                pattern = re.compile(
                    r'(?P<attr>[A-Z]+)'          # 1. 属性：任意大写字母串
                    r'(?P<op>[+-=])'              # 2. 方向：+ 或 -
                    r'(?P<val>[1-9]\d*)'         # 3. 数值：正整数（首位不能为 0）
                    r'(?:(?P<is_pct>%)(?P<pct_base>[bmr]))?'  # 4. 可选：% 紧跟 b/m/r
                )
                info = pattern.fullmatch(self.param).groupdict()
                info['attr'] = Effect.ATTRS.get(info['attr'], info['attr'].lower())
                info['is_pct'] = True if info['is_pct'] else False
                if info['is_pct']:
                    if info['pct_base'] == 'm' and info['attr'] not in ['hp', 'energy']:
                        info['pct_base'] = 'r'  # 非生命和能量属性，m视为r
                    elif not info['pct_base']:
                        info['pct_base'] = 'r'  # 默认百分比基于当前值
                return info
            case "add_buff":
                pass
            case "remove_buff":
                pass
            case "add_statu":
                pass
            case "remove_statu":
                pass
            case _:
                pass
    
    @classmethod
    def byList(cls, data: list) -> "Effect":
        """
        通过列表创建Effect实例
        :param data: [effect_type, param, mode] 格式的列表
        :return: Effect实例
        """
        if len(data) >= 3:
            return cls(effect_type=data[0], param=data[1], mode=data[2])
        else:
            raise ValueError("列表至少需要包含 effect_type, param 和 mode")
        
    @classmethod
    def byDict(cls, data: dict) -> "Effect":
        return cls(data.get["typs"], data.get["param"], data.get["mode"])

'''class Effect:
    """
    效果类，表示单个属性修改效果
    """

    TYPES = SimpleNamespace(
        ADD="add",
        MULTIPLY="multiply",
        OVERRIDE="override"
    )

    ATTACK_POWER = "atk"
    HEALTH_POINTS = "hp"
    SPEED = "speed"
    ENERGY = "energy"
    HATE_VALUE = "hate_value"

    def __init__(self, _attr: str, _value: float, _type: str = TYPES.ADD):
        """
        初始化效果
        :param attr: 属性名称 (例如: "atk", "hp", "speed")
        :param value: 效果值
        :param type: 效果类型 (例如: "add", "multiply", "override")
        """
        self.effect_attr = _attr
        self.effect_value = _value
        self.effect_type = _type

    def effectInfo(self) -> Tuple[str, float]:
        """
        返回效果信息
        :return: (属性名, 效果值) 元组
        """
        return (f"{self.effect_type}-{self.effect_attr}", self.effect_value)
    
    @classmethod
    def byDict(cls, data: dict) -> "Effect":
        """
        通过字典创建Effect实例
        :param data: 包含 attr, value, type 的字典
        :return: Effect实例
        """
        return cls(
            _attr=data.get("attr", ""),
            _value=data.get("value", 0.0),
            _type=data.get("type", "add")
        )
    
    @classmethod
    def byList(cls, data: list) -> "Effect":
        """
        通过列表创建Effect实例
        :param data: [attr, value, type] 格式的列表
        :return: Effect实例
        """
        if len(data) >= 3:
            return cls(_attr=data[0], _value=data[1], _type=data[2])
        elif len(data) == 2:
            return cls(_attr=data[0], _value=data[1], _type="add")
        else:
            raise ValueError("列表至少需要包含 attr 和 value")
    
    def __str__(self):
        return f"Effect({self.effect_attr}, {self.effect_value}, {self.effect_type})"
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other) -> bool:
        """
        判断两个Effect是否相同（通过属性名和类型判断）
        :param other: 另一个Effect对象
        :return: True表示相同，False表示不同
        """
        if not isinstance(other, Effect):
            return False
        return ((self.effect_attr == other.effect_attr and 
                self.effect_type == other.effect_type))
    
class InstantEffect(Effect):
    """
    即时效果类，表示一次性应用的效果
    """
    def __init__(self, _attr: str, _value: float, _type: str = Effect.TYPES.ADD):
        """
        初始化即时效果
        :param attr: 属性名称 (例如: "atk", "hp", "speed")
        :param value: 效果值
        :param type: 效果类型 (例如: "add", "multiply", "override")
        """
        super().__init__(_attr, _value, _type)
'''
class Buff:
    """
    增益/减益类，表示一个可叠加、有持续时间的效果组合
    """
    
    def __init__(self, name: str, effect_list: List[Effect], max_layer: int = 1, 
                 layer: int = 1, duration: int = -1):
        """
        初始化Buff
        :param name: Buff名称
        :param effect_list: 效果列表
        :param max_layer: 最大叠加层数
        :param layer: 当前层数
        :param duration: 持续回合数 (-1表示永久)
        """
        self.name = name
        self.effect_list = effect_list if effect_list else []
        self.max_layer = max_layer
        self.layer = min(layer, max_layer)
        self.initial_duration = duration
        self.duration = duration
    
    def getEffectDict(self) -> dict:
        """
        获取所有效果的字典表示，考虑层数加成
        :return: {属性名: 总效果值} 字典
        """
        effect_dict = {}
        for effect in self.effect_list:
            attr, value = effect.effectInfo()
            if attr in effect_dict:
                effect_dict[attr] += value * self.layer
            else:
                effect_dict[attr] = value * self.layer
        return effect_dict
    
    def getEffects(self) -> list:
        return self.effect_list
    
    def addLayer(self, num: int = 1):
        """
        增加Buff层数
        :param num: 增加的层数
        """
        self.layer = min(self.layer + num, self.max_layer)
        # 重置持续时间
        self.resetDuration()
    
    def resetDuration(self):
        """
        重置持续时间到初始值
        """
        self.duration = self.initial_duration
    
    def update(self):
        """
        更新Buff状态（每回合调用）
        如果有持续时间限制，则递减
        """
        if self.duration > 0:
            self.duration -= 1
    
    def isAlive(self) -> bool:
        """
        检查Buff是否仍然有效
        :return: True表示有效，False表示已失效
        """
        return self.duration != 0  # -1表示永久，>0表示还有时间，0表示失效
    
    def __eq__(self, other) -> bool:
        """
        判断两个Buff是否相同（通过名称判断）
        :param other: 另一个Buff对象
        :return: True表示相同，False表示不同
        """
        if not isinstance(other, Buff):
            return False
        return self.name == other.name and self.duration == other.duration
    
    def __str__(self):
        return f"Buff({self.name}, layer={self.layer}/{self.max_layer}, duration={self.duration})"
    
    def __repr__(self):
        return self.__str__()
    
    @classmethod
    def byDict(self):
        pass


class BuffList:
    """
    Buff列表类，管理角色身上的所有Buff
    """
    
    def __init__(self):
        """
        初始化空的Buff列表
        """
        self.buffs: List[Buff] = []
    
    def update(self):
        """
        更新所有Buff状态，移除失效的Buff
        """
        # 更新每个Buff
        for buff in self.buffs:
            buff.update()
        
        # 移除失效的Buff
        self.buffs = [buff for buff in self.buffs if buff.isAlive()]
    
    def getEffectDict(self) -> dict:
        """
        获取所有Buff的总效果字典
        :return: {属性名: 总效果值} 字典
        """
        total_effects = {}
        for buff in self.buffs:
            buff_effects = buff.getEffectDict()
            for attr, value in buff_effects.items():
                if attr in total_effects:
                    total_effects[attr] += value
                else:
                    total_effects[attr] = value
        return total_effects
    
    def getEffects(self) -> list:
        ls = []
        for buff in self.buffs:
            ls += buff.getEffects()
        return ls
    
    def addBuff(self, buff: Buff):
        """
        添加Buff到列表
        如果同名Buff已存在，则增加层数；否则添加新Buff
        :param buff: 要添加的Buff对象
        """
        # 检查是否已存在同名Buff
        for existing_buff in self.buffs:
            if existing_buff == buff:
                # 已存在，增加层数
                existing_buff.addLayer(buff.layer)
                return
        
        # 不存在，添加新Buff
        self.buffs.append(buff)
    
    def __str__(self):
        return f"BuffList({len(self.buffs)} buffs: {[str(b) for b in self.buffs]})"
    
    def __repr__(self):
        return self.__str__()

class Skill:
    """
    技能类，表示角色的技能
    self.info: dict - 存储技能的各种信息
    例如:
    {
        "id": "技能id",
        "name": "技能名称",
        "decription": "技能描述",
        "type": "技能种类",
        "trigger": "事件触发器",         //参照 事件文档.md
        "condition": [                  //参照 条件文档.md
            {
                "type": "条件类型",
                "param": "条件参数"
            },
            ...
        ],
        "effect": [                     //参照 效果文档.md
            {
                "type": "效果类型",
                "param": "效果参数",
                "mode": "生效模式"
            },
            ...
        ]
    }
    """
    
    def __init__(self, info: dict = None):
        self.info = {
            "id": info.get("id", "") if info else "",
            "name": info.get("name", "") if info else "",
            "decription": info.get("decription", "") if info else "",
            "type": info.get("type", "") if info else "",
            "trigger": info.get("trigger", "") if info else "",
            "condition": [Condition.byDict(c) for c in info.get("condition", [])] if info else [ALWAYS_CONDITION],
            "effect": [Effect.byDict(e) for e in info.get("effect", [])] if info else []
        }

    def canUse(self, character) -> bool:
        """
        检查角色是否可以使用该技能
        :param character: 角色对象
        :return: True表示可以使用，False表示不可以
        """
        if self.info["type"] == "positive":
            for condition in self.info["condition"]:
                if not condition.check(character=character):
                    return False
            return True
        return False

if __name__ == "__main__":
    
    pass