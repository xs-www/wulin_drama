import pygame
from util import *
from effect import BuffList, Buff, Effect
from keywords import keywordFactory

class Damage:
    """
    伤害类，表示一次伤害事件
    """
    def __init__(self, source: "Character", amount: int, damage_type: str = "physical"):
        """        
        初始化伤害事件
        :param self: 说明
        :param source: 伤害来源角色
        :type source: "Character"
        :param amount: 伤害数值
        :type amount: int
        :param damage_type: 伤害类型
        :type damage_type: str
        """
        self.source = source
        self.amount = amount
        self.damage_type = damage_type

class Entity(pygame.sprite.Sprite):
    """
    实体类，表示游戏中的基本单位
    """
    def __init__(self, attrs: dict):
        super().__init__()
        self.base_attrs = attrs if attrs else {
            "atk": 1,
            "hp": 10,
            "speed": 1
        }

    def setPosition(self, position):
        self.position = position

    def getHurt(self, damage):

        self.health_points -= damage
        if self.health_points < 0:
            self.health_points = 0

    def isAlive(self) -> bool:

        return self.health_points > 0

    def move(self, new_position):
        self.position = new_position

    def __str__(self):
        return f"Entity(Health: {self.health_points}, Position: {self.position})"

## todo
## 重构 Character 类
## base_attr, current_attr, max_attr
## 支持Effect, Buff 等机制
class Character(pygame.sprite.Sprite):
    """
    角色类，表示游戏中的棋子
    """
    def __init__(self, attrs: dict):
        super().__init__()
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

        self.info: dict = {
            "id": attrs.get("id", "0000"),
            "position": ("None", -1),  # (row_name, index)
            "team_id": None,
            "name": attrs.get("name", "Unknown"),
            "price": attrs.get("price", 1),
            "position_constraint": attrs.get("avaliable_location", []),
            "weapon_constraint": attrs.get("weapon", []),
            "fetters": attrs.get("fetter", []),
            "max_initiative": 10
        }

        self.buffs = BuffList()

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
        if key in self.base_attrs:
            return self.base_attrs[key]
        elif key in self.info:
            return self.info[key]
        elif key in self.current_attrs:
            return self.current_attrs[key]
        else:
            raise AttributeError(f"Attribute '{key}' not found")
        
    def setAttr(self, key: str, value):
        if key in self.base_attrs:
            self.base_attrs[key] = value
            return True
        elif key in self.info:
            self.info[key] = value
            return True
        elif key in self.current_attrs:
            self.current_attrs[key] = value
            return True
        else:
            raise AttributeError(f"Attribute '{key}' not found")
    
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
        damage_amount = self.getAttr("current_atk")
        return Damage(source=self, amount=damage_amount, damage_type="physical")
        
    def getHateValue(self) -> int:
        return self.getAttr("current_hate_value") if self.isAlive() else 0
    
    def applyBuff(self, buff: Buff):
        self.buffs.addBuff(buff)
    
    def applyEffect(self, effect: Effect):
        match effect.effect_type:
            case "modify_attr":
                eff = effect.emphasize()
                attr = eff['attr']
                op = eff['op']
                val = int(eff['val'])
                is_pct = eff['is_pct']
                pct_base = eff['pct_base']
                if is_pct:
                    base_value = 0
                    match pct_base:
                        case 'b':
                            base_value = self.getAttr("base_" + attr, 0)
                        case 'm':
                            base_value = self.getAttr("max_" + attr)
                        case 'r':
                            base_value = self.getAttr("current_" + attr)
                    val = base_value * val // 100
                else:
                    val = val
                current_value = self.getAttr("current_" + attr)
                match op:
                    case '+':
                        new_value = current_value + val
                    case '-':
                        new_value = current_value - val
                    case '=':
                        new_value = val
                self.setAttr("current_" + attr, new_value)
            case _:
                pass

    def getEffectDict(self) -> dict:
        return mergeDicts([self.buffs.getEffectDict()])

    def isAlive(self) -> bool:
        return self.getInGameAttr("current_hp") > 0
    
    def getHurt(self, damage: Damage):
        em.broadcast('beforeGetHurt', target=self, damage=damage)
        em.broadcast('onGetHurt', target=self, damage=damage)
        current_hp = self.getInGameAttr("current_hp")
        if damage.amount > 0:
            log.console(f"{self.getAttr('name')} 受到 {damage.amount} 点{damage.damage_type}伤害！", "DAMAGE")
            self.setInGameAttr("current_hp", max(0, current_hp - damage.amount))
            em.broadcast('afterGetHurt', target=self, damage=damage)
        
    @staticmethod
    def infoList(char: "Character" = None) -> list[str]:
        if isinstance(char, Character):
            if char.isAlive():
                il = [
                    "+" + "-" * 11 + "+",
                    "|" + " " * 11 + "|",
                    "|" + " " * 11 + "|",
                    "| " + str(char.getInGameAttr("atk")).rjust(4) + "/" + str(char.getInGameAttr("current_hp")).ljust(4) + " |",
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
    char = Character.byId("0002")
    char.draw()