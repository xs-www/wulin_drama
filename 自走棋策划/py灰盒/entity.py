import pygame
from util import *
from effect import BuffList, Buff, Effect

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
            "fetters": attrs.get("fetter", []),
            "base_hate_value": attrs.get("hate_value", 1),
            "price": attrs.get("price", 1),
            "hate_bias_matrix": attrs.get("hate_matrix", [[1, 1, 1],[1, 1, 1],[1, 1, 1]]),
            "max_energy": attrs.get("energy", 3),
            "position_constraint": attrs.get("avaliable_location", []),
            "weapon_constraint": attrs.get("weapon", []),
            "max_initiative": 10
        }

        self.info: dict = {
            "position": ("None", -1),  # (row_name, index)
            "team_id": None,
            "name": attrs.get("name", "Unknown")
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

        self.equipments: dict = {
            "weapon": None,
            "armor": None,
            "accessory": None
        }

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
        else:
            raise AttributeError(f"Attribute '{key}' not found")
        
    def setAttr(self, key: str, value):
        if key in self.base_attrs:
            self.base_attrs[key] = value
            return True
        elif key in self.info:
            self.info[key] = value
            return True
        else:
            raise AttributeError(f"Attribute '{key}' not found")
        
    def getInGameAttr(self, key: str):
        if key in self.in_game_attrs:
            return self.in_game_attrs[key]
        else:
            raise AttributeError(f"In-game attribute '{key}' not found")
        
    def setInGameAttr(self, key: str, value):
        if key in self.in_game_attrs:
            self.in_game_attrs[key] = value
            return True
        else:
            raise AttributeError(f"In-game attribute '{key}' not found")

    def getAttackDamage(self) -> Damage:
        damage_amount = self.getInGameAttr("atk")
        return Damage(source=self, amount=damage_amount, damage_type="physical")
        
    def getHateValue(self) -> int:
        return self.getInGameAttr("hate_value") if self.isAlive() else 0
    
    def applyBuff(self, buff: Buff):
        self.buffs.addBuff(buff)
    
    def applyEffect(self, effect: Effect):
        pass


    def getEffectDict(self) -> dict:
        return mergeDicts([self.buffs.getEffectDict()])

    def isAlive(self) -> bool:
        return self.getInGameAttr("current_hp") > 0
    
    #@em.on('get_hurt')
    def getHurt(self, damage: Damage):
        #em.broadcast('before_get_hurt', target=self, damage=damage)
        current_hp = self.getInGameAttr("current_hp")
        current_hp -= damage.amount
        if current_hp < 0:
            current_hp = 0
        self.in_game_attrs["current_hp"] = current_hp
        #em.broadcast('after_get_hurt', target=self, damage=damage)
        
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

    @classmethod
    def byId(cls, char_id: str):

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