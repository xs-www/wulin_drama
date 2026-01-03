import pygame
from util import *

class Damage:

    def __init__(self, source: "Character", amount: int, damage_type: str = "physical"):
        self.source = source
        self.amount = amount
        self.damage_type = damage_type

class Entity(pygame.sprite.Sprite):

    def __init__(self, attrs: dict):
        super().__init__()
        self.attrs = attrs if attrs else {
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

    def __init__(self, attrs: dict):
        super().__init__()
        self.attrs: dict = {
            "base_atk": attrs.get("attack_power", 1),
            "base_hp": attrs.get("health_points", 10),
            "base_speed": attrs.get("speed", 1),
            "fetters": attrs.get("fetter", []),
            "base_hate_value": attrs.get("hate_value", 1),
            "price": attrs.get("price", 1),
            "hate_bias_matrix": attrs.get("hate_matrix", [[1, 1, 1],[1, 1, 1],[1, 1, 1]]),
            "max_energy": attrs.get("energy", 3),
            "position_constraint": attrs.get("avaliable_location", []),
            "weapon_constraint": attrs.get("weapon", [])
        }

        self.info: dict = {
            "position": ("None", -1),  # (row_name, index)
            "team_id": None,
            "name": attrs.get("name", "Unknown")
        }

        self.buffs: list = []

        self.in_game_attrs: dict = {
            "max_hp": self.attrs["base_hp"],
            "current_hp": self.attrs["base_hp"],
            "atk": self.attrs["base_atk"],
            "speed": self.attrs["base_speed"],
            "max_energy": self.attrs["max_energy"],
            "current_energy": 0,
            "hate_value": self.attrs["base_hate_value"]
        }

        self.equipments: dict = {
            "weapon": None,
            "armor": None,
            "accessory": None
        }

    # @todo
    def updateInGameAttrs(self):
        pass

    def getAttr(self, key: str):
        if key in self.attrs:
            return self.attrs[key]
        elif key in self.info:
            return self.info[key]
        else:
            raise KeyError(f"Attribute '{key}' not found")
        
    def setAttr(self, key: str, value):
        if key in self.attrs:
            self.attrs[key] = value
            return True
        elif key in self.info:
            self.info[key] = value
            return True
        else:
            raise KeyError(f"Attribute '{key}' not found")
        
    def getInGameAttr(self, key: str):
        if key in self.in_game_attrs:
            return self.in_game_attrs[key]
        else:
            raise KeyError(f"In-game attribute '{key}' not found")

    def getAttackDamage(self) -> Damage:
        damage_amount = self.getInGameAttr("atk")
        return Damage(source=self, amount=damage_amount, damage_type="physical")
        
    def getHateValue(self) -> int:
        return self.getInGameAttr("hate_value")
    
    def addBuff(self, buff: "Buff"):
        self.buffs.append(buff)

    def isAlive(self) -> bool:
        return self.getInGameAttr("current_hp") > 0
    
    @em.on('get_hurt')
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
            il = [
                "+" + "-" * 11 + "+",
                "|" + " " * 11 + "|",
                "|" + " " * 11 + "|",
                "| " + str(char.getInGameAttr("atk")).rjust(4) + "/" + str(char.getInGameAttr("current_hp")).ljust(4) + " |",
                "+" + "-" * 11 + "+"
            ]
        else:
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

    @classmethod
    def byId(cls, char_id: str):

        char_attrs = loadCharacterAttrs(char_id)
        new_char = Character(char_attrs)

        return new_char

# @todo
class Equipment:

    def __init__(self):
        pass



if __name__ == "__main__":
    char = Character.byId("0002")
    char.draw()