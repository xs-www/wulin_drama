"""
effect.py - 实现效果(Effect)、增益/减益(Buff)和增益列表(BuffList)的管理系统
"""

from typing import Tuple, List, Dict, Optional


class Effect:
    """
    效果类，表示单个属性修改效果
    """
    
    def __init__(self, attr: str, value: float, type: str):
        """
        初始化效果
        :param attr: 属性名称 (例如: "atk", "hp", "speed")
        :param value: 效果值
        :param type: 效果类型 (例如: "add", "multiply", "override")
        """
        self.attr = attr
        self.value = value
        self.type = type
    
    def effectInfo(self) -> Tuple[str, float]:
        """
        返回效果信息
        :return: (属性名, 效果值) 元组
        """
        return (self.attr, self.value)
    
    @classmethod
    def byDict(cls, data: dict) -> "Effect":
        """
        通过字典创建Effect实例
        :param data: 包含 attr, value, type 的字典
        :return: Effect实例
        """
        return cls(
            attr=data.get("attr", ""),
            value=data.get("value", 0.0),
            type=data.get("type", "add")
        )
    
    @classmethod
    def byList(cls, data: list) -> "Effect":
        """
        通过列表创建Effect实例
        :param data: [attr, value, type] 格式的列表
        :return: Effect实例
        """
        if len(data) >= 3:
            return cls(attr=data[0], value=data[1], type=data[2])
        elif len(data) == 2:
            return cls(attr=data[0], value=data[1], type="add")
        else:
            raise ValueError("列表至少需要包含 attr 和 value")
    
    def __str__(self):
        return f"Effect({self.attr}, {self.value}, {self.type})"
    
    def __repr__(self):
        return self.__str__()


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
        return self.name == other.name
    
    def __str__(self):
        return f"Buff({self.name}, layer={self.layer}/{self.max_layer}, duration={self.duration})"
    
    def __repr__(self):
        return self.__str__()


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


if __name__ == "__main__":
    # 测试代码
    print("=== 测试 Effect 类 ===")
    
    # 通过构造函数创建
    effect1 = Effect("atk", 10.0, "add")
    print(f"effect1: {effect1}")
    print(f"effect1.effectInfo(): {effect1.effectInfo()}")
    
    # 通过字典创建
    effect2 = Effect.byDict({"attr": "hp", "value": 50.0, "type": "add"})
    print(f"effect2: {effect2}")
    
    # 通过列表创建
    effect3 = Effect.byList(["speed", 5.0, "multiply"])
    print(f"effect3: {effect3}")
    
    print("\n=== 测试 Buff 类 ===")
    
    # 创建一个有两个效果的Buff
    buff1 = Buff("力量祝福", [effect1, effect2], max_layer=3, layer=1, duration=5)
    print(f"buff1: {buff1}")
    print(f"buff1.getEffectDict(): {buff1.getEffectDict()}")
    
    # 增加层数
    buff1.addLayer(2)
    print(f"增加2层后: {buff1}")
    print(f"buff1.getEffectDict(): {buff1.getEffectDict()}")
    
    # 更新状态
    buff1.update()
    print(f"更新一次后: {buff1}")
    print(f"buff1.isAlive(): {buff1.isAlive()}")
    
    print("\n=== 测试 BuffList 类 ===")
    
    buff_list = BuffList()
    print(f"初始: {buff_list}")
    
    # 添加第一个Buff
    buff_list.addBuff(buff1)
    print(f"添加buff1后: {buff_list}")
    print(f"总效果: {buff_list.getEffectDict()}")
    
    # 添加同名Buff（应该叠加层数）
    buff2 = Buff("力量祝福", [effect1, effect2], max_layer=3, layer=1, duration=5)
    buff_list.addBuff(buff2)
    print(f"添加同名buff后: {buff_list}")
    print(f"总效果: {buff_list.getEffectDict()}")
    
    # 添加不同名的Buff
    buff3 = Buff("速度祝福", [effect3], max_layer=1, layer=1, duration=3)
    buff_list.addBuff(buff3)
    print(f"添加buff3后: {buff_list}")
    print(f"总效果: {buff_list.getEffectDict()}")
    
    # 更新BuffList（模拟回合结束）
    print("\n=== 模拟3个回合 ===")
    for i in range(3):
        buff_list.update()
        print(f"回合{i+1}结束后: {buff_list}")
        print(f"总效果: {buff_list.getEffectDict()}")
    
    # 再更新2次，速度祝福应该消失
    for i in range(2):
        buff_list.update()
        print(f"回合{i+4}结束后: {buff_list}")
        print(f"总效果: {buff_list.getEffectDict()}")
    
    print("\n=== 测试永久Buff ===")
    permanent_buff = Buff("永久力量", [Effect("atk", 100.0, "add")], max_layer=1, layer=1, duration=-1)
    buff_list2 = BuffList()
    buff_list2.addBuff(permanent_buff)
    print(f"添加永久buff: {buff_list2}")
    
    for i in range(5):
        buff_list2.update()
        print(f"更新{i+1}次后: {buff_list2}")
    
    print("\n测试完成！")
