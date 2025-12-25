import pygame
from util import *

class Character():
    FONT = None          # 类级缓存，避免重复创建
    COLOR_BOX   = (50, 200, 50)
    COLOR_TEXT  = (0, 0, 0)

    def __init__(self, name, attack_power=4, health_points=8, speed=2, fetter=None, hate_value=0, avaliable_location=None, price=0, hate_matrix=None, energy=0, weapon=None):

        self.name = name
        self.attack_power = attack_power
        self.health_points = health_points
        self.speed = speed
        self.fetter = fetter if fetter else []
        self.hate_value = hate_value
        self.avaliable_location = avaliable_location if avaliable_location else []
        self.price = price
        self.hate_matrix = hate_matrix if hate_matrix else []
        self.energy = energy
        self.weapon = weapon

        self.position = ("None", -1)  # (row_name, index)
        self.team_id = None

    def setPosition(self, position):
        self.position = position

    def setTeamId(self, team_id):
        self.team_id = team_id

    def getSpeed(self) -> int:
        return self.speed
    
    def getTeamId(self):
        return self.team_id

    def getHateValue(self) -> int:
        row_idx = self.position[0]
        
        return (self.hate_value + {
            "front": 2,
            "middle": 1,
            "back": 0
        }[row_idx])
    
    def __str__(self):
        atk_str = f"{self.attack_power:4d}"
        hp_str = f"{self.health_points}" + " " * (4 - len(f"{self.health_points}"))
        return atk_str + "/" + hp_str
    
    def __lt__(self, other: 'Character') -> bool:
        return self.speed < other.speed
    
    @classmethod
    def characterFromId(cls, char_id: chr) -> 'Character':

        character_config = load_character_config(char_id)
        new_character = cls(
            name=character_config.get("name", "Unknown"),
            attack_power=character_config.get("attack_power", 4),
            health_points=character_config.get("health_points", 8),
            speed=character_config.get("speed", 2),
            fetter=character_config.get("fetter", []),
            hate_value=character_config.get("hate_value", 1),
            avaliable_location=character_config.get("avaliable_location", []),
            price=character_config.get("price", 1),
            hate_matrix=character_config.get("hate_matrix", [[1, 1, 1],[1, 1, 1],[1, 1, 1]]),
            energy=character_config.get("energy", 0),
            weapon=character_config.get("weapon", None),
        )

        return new_character
    

class BattleCharacter(Character):
    def __init__(self, character: Character):
        super().__init__(
            name=character.name,
            attack_power=character.attack_power,
            health_points=character.health_points,
            speed=character.speed,
            fetter=character.fetter,
            hate_value=character.hate_value,
            avaliable_location=character.avaliable_location,
            price=character.price,
            hate_matrix=character.hate_matrix,
            energy=character.energy,
            weapon=character.weapon
        )

        self.team_id = character.team_id
        self.position = character.position
        self.base_hate_value = character.hate_value
        self.current_health = character.health_points

        self.alive = True

    def isAlive(self) -> bool:
        return self.alive

    def getHurt(self, damage):
        self.current_health -= damage
        if self.current_health <= 0:
            self.current_health = 0
            self.alive = False

    def getHateValue(self) -> int:
        row_idx = self.position[0]
        
        return (self.hate_value + {
            "front": 2,
            "middle": 1,
            "back": 0
        }[row_idx]) if self.alive else 0
    
    def getAttackPower(self) -> int:
        return self.attack_power if self.alive else 0
    
    def getInfo(self) -> str:
        return f"{self.name} (ATK: {self.attack_power}, HP: {self.current_health}/{self.health_points}, SPD: {self.speed})"