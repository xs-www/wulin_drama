import pygame
from util import *
from effect import BuffList, Buff, Effect
from keywords import keywordFactory

class Entity(pygame.sprite.Sprite):
    """
    实体类，表示游戏中的基本单位
    """
    def __init__(self, attrs: dict = None):
        super().__init__()
        self.attrs = attrs if attrs is not None else {}

    def setAttr(self, key, value):
        """
        设置属性值，支持嵌套 key，如 "aaa.bbb.ccc" -> attrs['aaa']['bbb']['ccc']
        仅当目标 key 存在时设置，否则抛出 AttributeError（保持原有行为）。
        """
        parts = key.split('.') if isinstance(key, str) else [key]
        node = self.attrs
        # 遍历到父节点
        for p in parts[:-1]:
            if isinstance(node, dict) and p in node:
                node = node[p]
            else:
                raise AttributeError(f"Attribute '{key}' not found")
        last = parts[-1]
        if isinstance(node, dict) and last in node:
            node[last] = value
            return True
        else:
            raise AttributeError(f"Attribute '{key}' not found")
        
    def getAttr(self, key, value = None):
        """
        支持嵌套查询，例如 "aaa.bbb" 会返回 attrs['aaa']['bbb']，找不到时抛出 AttributeError。
        """
        if '.' in key:
            parts = key.split('.') if isinstance(key, str) else [key]
            node = self.attrs
            for p in parts:
                if isinstance(node, dict) and p in node:
                    node = node[p]
                else:
                    raise AttributeError(f"Attribute '{key}' not found")
            return node
        else:
            def dfs(node):
                if isinstance(node, dict):
                    for k, v in node.items():
                        if k == key:
                            return v
                        res = dfs(v)
                        if res is not None:
                            return res
                return None
            res = dfs(self.attrs)
            if res is not None:
                return res

    def addAttr(self, key, value):
        """
        添加属性值，支持嵌套 key，如 "aaa.bbb.ccc" -> attrs['aaa']['bbb']['ccc']
        如果中间节点不存在则创建，最终设置目标 key 的值为 value。
        """
        parts = key.split('.') if isinstance(key, str) else [key]
        node = self.attrs
        for p in parts[:-1]:
            if isinstance(node, dict):
                if p not in node:
                    node[p] = {}
                node = node[p]
            else:
                raise AttributeError(f"Cannot create nested attribute '{key}'")
        last = parts[-1]
        if isinstance(node, dict):
            node[last] = value
            return True
        else:
            raise AttributeError(f"Cannot set attribute '{key}'")

    def applyEffect(self, effect: Effect):
        log.console(f"{self} applyEffect called with effect: {effect}")
        

class Damage(Entity):
    """
    伤害类，表示一次伤害事件
    """
    def __init__(self, source: "Character", damage: int, damage_type: str = "physical"):
        """        
        初始化伤害事件
        :param self: 说明
        :param source: 伤害来源角色
        :type source: "Character"
        :param damage: 伤害数值
        :type damage: int
        :param damage_type: 伤害类型
        :type damage_type: str
        """
        super().__init__()
        self.addAttr("source", source)
        self.addAttr("damage", damage)
        self.addAttr("damage_type", damage_type)
    
    def applyEffect(self, effect):
        super().applyEffect(effect)
        if effect.effect_type == "modify_attr":
            eff = effect.parse()
            op = eff['op']
            val = int(eff['val'])
            is_pct = eff['is_pct']
            if is_pct:
                base_value = self.getAttr("damage")
                val = base_value * val // 100
            else:
                val = val
            current_value = self.getAttr("damage")
            match op:
                case '+':
                    new_value = current_value + val
                case '-':
                    new_value = current_value - val
                case '=':
                    new_value = val
            self.setAttr("damage", new_value)

## todo
## 重构 Character 类
## base_attr, current_attr, max_attr
## 支持Effect, Buff 等机制
class Character(Entity):
    """
    角色类，表示游戏中的棋子
    """
    def __init__(self, attrs: dict):
        super().__init__()
        self.addAttr("base.atk", attrs.get("attack_power", 1))
        self.addAttr("base.hp", attrs.get("health_points", 10))
        self.addAttr("base.speed", attrs.get("speed", 1))
        self.addAttr("base.critical_rate", attrs.get("critical_rate", 0.0))
        self.addAttr("base.critical_damage", attrs.get("critical_damage", 1.5))
        self.addAttr("base.armor", attrs.get("armor", 0))
        self.addAttr("base.energy", attrs.get("energy", 0))
        self.addAttr("base.hate_value", attrs.get("hate_value", 1))

        self.addAttr("max.hp", attrs.get("health_points", 10))
        self.addAttr("max.energy", attrs.get("energy", 3))
        self.addAttr("max.initiative", 10)

        self.addAttr("hate_bias_matrix", attrs.get("hate_matrix", [[1, 1, 1],[1, 1, 1],[1, 1, 1]]))

        self.addAttr("info.id", attrs.get("id", "0000"))
        self.addAttr("info.position", ("None", -1))  # (row_name
        self.addAttr("info.team_id", None)
        self.addAttr("info.name", attrs.get("name", "Unknown"))
        self.addAttr("info.price", attrs.get("price", 1))
        self.addAttr("info.position_constraint", attrs.get("avaliable_location", []))
        self.addAttr("info.weapon_constraint", attrs.get("weapon", []))
        self.addAttr("info.fetters", attrs.get("fetter", []))

        self.addAttr("current.atk", attrs.get("attack_power", 1))
        self.addAttr("current.hp", attrs.get("health_points", 10))
        self.addAttr("current.speed", attrs.get("speed", 1))
        self.addAttr("current.critical_rate", 0.0)
        self.addAttr("current.critical_damage", 1.5)
        self.addAttr("current.armor", 0)
        self.addAttr("current.energy", 0)
        self.addAttr("current.hate_value", attrs.get("hate_value", 1))
        self.addAttr("current.initiative", 0)

        self.base_attrs: dict = {
            "base_atk": attrs.get("attack_power", 1),
            "base_hp": attrs.get("health_points", 10),
            "base_speed": attrs.get("speed", 1),
            "base_critical_rate": attrs.get("critical_rate", 0.0),
            "base_critical_damage": attrs.get("critical_damage", 1.5),
            "base_armor": attrs.get("armor", 0),
            "base_energy": attrs.get("energy", 0),
            "base_hate_value": attrs.get("hate_value", 1),

            "max_hp": attrs.get("health_points", 10),
            "max_energy": attrs.get("energy", 3),

            "hate_bias_matrix": attrs.get("hate_matrix", [[1, 1, 1],[1, 1, 1],[1, 1, 1]]),
        }

        self.buffs = BuffList()

        # delete later
        self.in_game_attrs: dict = {
            "initiative": 0,
            "max_initiative": 10,
            "max_hp": self.base_attrs["base_hp"],
            "current_hp": self.base_attrs["base_hp"],
            "atk": self.base_attrs["base_atk"],
            "speed": self.base_attrs["base_speed"],
            "max_energy": self.base_attrs["max_energy"],
            "current_energy": 0,
            "hate_value": self.base_attrs["base_hate_value"]
        }

        # delete later
        self.current_attrs = {
            "current_atk": self.base_attrs["base_atk"],
            "current_hp": self.base_attrs["base_hp"],
            "current_speed": self.base_attrs["base_speed"],
            "current_critical_rate": 0.0,
            "current_critical_damage": 1.5,
            "current_armor": 0,
            "current_energy": 0,
            "current_hate_value": self.base_attrs["base_hate_value"],
            "initiative": 0
        }

        self.equipments: dict = {
            "weapon": None,
            "armor": None,
            "accessory": None
        }

        self.status: list = []
        self.skills: list = []

        self.keywords: list = []
        self.keywords_dict = {}
    
    def hasStatus(self, status_name: str) -> bool:
        return status_name in self.status
    
    def addStatus(self, status_name: str):
        if status_name not in self.status:
            self.status.append(status_name)
    
    def removeStatus(self, status_name: str):
        if status_name in self.status:
            self.status.remove(status_name)

    def updateAttrs(self):
        effects = self.getAllEffects(effect_type = "modify_attr")
        attr_bouns = {}
        for e in effects:
            info = e.parse()


    # @todo
    def updateInGameAttrs(self):
        effect_dict = self.getEffectDict()
        bonus_dict = {
            "max_hp": 0,
            "current_hp": 0,
            "atk": 0,
            "speed": 0,
            "current_energy": 0,
            "hate_value": 0
        }
        effect_to_bonus = {
            "hp": "max_hp",
            "atk": "atk",
            "speed": "speed",
            "energy": "current_energy",
            "hate_value": "hate_value"
        }
        for attr, value in self.in_game_attrs.items():
            bonus_type, attr_name = tuple(attr.split("_", 1))
            if bonus_type == Effect.ADD:
                bonus_dict[attr] += effect_dict.get(attr, 0)
            elif bonus_type == Effect.MULTIPLY:
                bonus_dict[attr] += self.base_attrs["base_" + attr_name] * effect_dict.get(attr, 0)
        pass
    
    
    def getAttr(self, key: str):
        super().getAttr(key)
        
    def setAttr(self, key: str, value):
        before_value = super().getAttr(key)
        if before_value != value:
            super().setAttr(key, value)
            em.broadcast('onAttrChange', character=self, attr=key, before=before_value, after=value)

    # delete later
    def getInGameAttr(self, key: str):
        if key in self.in_game_attrs:
            return self.in_game_attrs[key]
        else:
            raise AttributeError(f"In-game attribute '{key}' not found")
    
    # delete later
    def setInGameAttr(self, key: str, value):
        if key in self.in_game_attrs:
            self.in_game_attrs[key] = value
            return True
        else:
            raise AttributeError(f"In-game attribute '{key}' not found")

    def getAttackDamage(self) -> Damage:
        damage_amount = self.getAttr("current.atk")
        return Damage(source=self, damage=damage_amount, damage_type="physical")
        
    def getHateValue(self) -> int:
        return self.getAttr("current.hate_value") if self.isAlive() else 0

    def applyBuff(self, buff: Buff):
        self.buffs.addBuff(buff)
        self.updateAttrs()

    def getResultofEffect(self, eff: dict) -> dict:
        attr = eff['attr']
        op = eff['op']
        val = int(eff['val'])
        is_pct = eff['is_pct']
        pct_base = eff['pct_base']
        if is_pct:
            base_value = 0
            match pct_base:
                case 'b':
                    base_value = self.getAttr("base." + attr)
                case 'm':
                    base_value = self.getAttr("max." + attr)
                case 'r':
                    base_value = self.getAttr("current." + attr)
            val = base_value * val // 100
        else:
            val = val
        match op:
            case '+':
                new_value = val
            case '-':
                new_value = -val
        res = {}
        res[f"current.{attr}"] = new_value
        return res

    def applyEffect(self, effect: Effect):
        super().applyEffect(effect)
        match effect.effect_type:
            case "modify_attr":
                eff = effect.parse()
                attr = eff['attr']
                op = eff['op']
                val = int(eff['val'])
                is_pct = eff['is_pct']
                pct_base = eff['pct_base']
                if is_pct:
                    base_value = 0
                    match pct_base:
                        case 'b':
                            base_value = self.getAttr("base." + attr)
                        case 'm':
                            base_value = self.getAttr("max." + attr)
                        case 'r':
                            base_value = self.getAttr("current." + attr)
                    val = base_value * val // 100
                else:
                    val = val
                current_value = self.getAttr("current." + attr)
                match op:
                    case '+':
                        new_value = current_value + val
                    case '-':
                        new_value = current_value - val
                    case '=':
                        new_value = val
                self.setAttr("current." + attr, new_value)
            case _:
                pass

    def getAllEffects(self, effect_type = None) -> list:
        ls = [self.buffs.getEffects()]

        if effect_type:
            ls = [ele for ele in ls if ele.effect_type == effect_type]
        return ls

    def getEffectDict(self) -> dict:
        return mergeDicts([self.buffs.getEffectDict()])

    def isAlive(self) -> bool:
        return self.getAttr("current.hp") > 0

    def getHurt(self, damage: Damage):
        em.broadcast('beforeGetHurt', target=self, damage=damage)
        em.broadcast('onGetHurt', target=self, damage=damage)
        current_hp = self.getAttr("current.hp")
        if damage.getAttr("damage") > 0:
            log.console(f"{self.getAttr('name')} 受到 {damage.getAttr('damage')} 点{damage.getAttr('damage_type')}伤害！", "DAMAGE")
            self.setAttr("current.hp", max(0, current_hp - damage.getAttr("damage")))
            em.broadcast('afterGetHurt', target=self, damage=damage)
        
    @staticmethod
    def infoList(char: "Character" = None) -> list[str]:
        if isinstance(char, Character):
            if char.isAlive():
                il = [
                    "+" + "-" * 11 + "+",
                    "|" + " " * 11 + "|",
                    "|" + " " * 11 + "|",
                    "| " + str(char.getAttr("current.atk")).rjust(4) + "/" + str(char.getAttr("current.hp")).ljust(4) + " |",
                    "+" + "-" * 11 + "+"
                ]
                return il
        il = [
            "+" + "-" * 11 + "+",
            "|" + " " * 11 + "|",
            "|" + " " * 11 + "|",
            "|" + " " * 11 + "|",
            "+" + "-" * 11 + "+"
        ]
        return il
    
    def draw(self, type = "terminal", screen = None, position = (0, 0)):
        if type == "terminal":
            for line in Character.infoList(self):
                print(line)
        elif type == "pygame" and screen is not None:
            pass

    def rollInitiative(self):
        self.setInGameAttr("initiative", roll(self.getInGameAttr("max_initiative")))

    def addKeyword(self, keyword_name: str):
        keyword = keywordFactory(keyword_name)(self)
        self.keywords.append(keyword)
        self.keywords_dict[keyword_name] = keyword

    def removeKeyword(self, keyword_instance):
        if keyword_instance in self.keywords:
            self.keywords.remove(keyword_instance)
            return True
        return False

    def doAct(self):
        pass

    @classmethod
    def byId(cls, char_id):

        if not isinstance(char_id, str):
            char_id = str(char_id).zfill(4)
        char_attrs = loadCharacterAttrs(char_id)
        new_char = Character(char_attrs)

        return new_char
    
    def __lt__(self, other: "Character"):
        return self.getInGameAttr("speed") + self.getInGameAttr("initiative") < other.getInGameAttr("speed") + other.getInGameAttr("initiative")

# @todo
class Equipment:

    def __init__(self):
        pass



if __name__ == "__main__":

    pass