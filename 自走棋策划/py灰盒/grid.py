#from character import Character, BattleCharacter
import uuid
import pygame
from util import em
from entity import Character

class GameRow:
    def __init__(self, idx = 0, max_length=3):
        self.entities :list[Character | None] = [None] * max_length
        self.max_length = max_length
        self.idx = idx

    def setCharacter(self, character: Character, idx: int = -1):
        if idx == -1:
            for i in range(self.max_length):
                if self.entities[i] is None:
                    self.entities[i] = character
                    return True
            return False
        else:
            idx -= 1  # Convert to 0-based index
            if 0 <= idx < self.max_length and self.entities[idx] is None:
                self.entities[idx] = character
                return True
            else:
                return False
            
    def removeCharacter(self, character: Character) -> bool:
        try:
            idx = self.entities.index(character)
            self.entities[idx] = None
            return True
        except ValueError:
            return False
    
    def removeCharacterByPosition(self, position: int) -> bool:
        idx = position - 1  # Convert to 0-based index
        if 0 <= idx < self.max_length and self.entities[idx] is not None:
            self.entities[idx] = None
            return True
        else:
            return False
    
    def getPosition(self, character: Character) -> int:
        try:
            return (self.idx, self.entities.index(character) + 1)
        except ValueError:
            return -1
        
    def getCharacterByPosition(self, position: int) -> Character | None:
        idx = position - 1  # Convert to 0-based index
        if 0 <= idx < self.max_length:
            return self.entities[idx]
        else:
            return None
        
    def getHateValue(self) -> list:
        hate_list = [entity.getHateValue() if entity is not None else 0 for entity in self.entities]
        return hate_list
    
    def getEntities(self) -> list:
        return [entity for entity in self.entities if entity is not None]

    def __str__(self):
        return f"GameRow(Entities: {[str(e) for e in self.entities]})"
    
    def isAllDead(self) -> bool:
        for entity in self.entities:
            if isinstance(entity, Character) and entity.isAlive():
                return False
        return True
    
    def isEmpty(self) -> bool:
        for entity in self.entities:
            if entity is not None:
                return False
        return True
    
    def infoList(self) -> list[str]:
        il = []
        for e in self.entities:
            new_il = Character.infoList(e)
            if len(il) > 0:
                for i in range(len(il)):
                    il[i] += new_il[i][1:]
            else:
                il = new_il
        return il
    
    def draw(self, draw_type = "terminal", screen = None, position = (0, 0)):
        match draw_type:
            case "terminal":
                for i in range(self.max_length):
                    print(str(i+1).rjust(7) if i == 0 else str(i+1).rjust(12), end="")
                print()
                for line in self.infoList():
                    print(line)
            case "pygame":
                pass
    
    @classmethod
    def byList(cls, ls):
        new_row = cls(max_length=len(ls))
        new_row.entities = ls
        return new_row

class GameGrid:
    def __init__(self, team_id=None):
        self.team_id = team_id if team_id is not None else uuid.uuid4()
        self.grid = {
            "front": GameRow(1),
            "middle": GameRow(2),
            "back": GameRow(3),
            "bench": GameRow(4)
        }

    def infoList(self) -> list[str]:
        il = []
        for row_name in ["front", "middle", "back", "bench"]:
            game_row = self.grid[row_name]
            row_il = game_row.infoList()
            for i in range(len(row_il)):
                if i == 2:
                    prefix = row_name.capitalize().ljust(8, ' ')
                else:
                    prefix = " " * 8
                row_il[i] = prefix + row_il[i]
            if len(il) > 0:
                il += row_il[1:]
            else:
                il = row_il
        return il

    def draw(self, draw_type = "terminal", screen = None, position = (0, 0), reverse=False):
        il = self.infoList()
        if reverse:
            il.reverse()
        match draw_type:
            case "terminal":
                for line in il:
                    print(line)
            case "pygame":
                pass

    def setCharacter(self, character: Character, row: str, idx: int = -1):
        if row in self.grid:
            if self.grid[row].setCharacter(character, idx):
                position = (row, self.grid[row].getPosition(character)[1])
                character.setAttr("info.position", position)
                character.setAttr("info.team_id", self.team_id)
                return True
        else:
            raise ValueError("Invalid row name")
        
    def getCharacterList(self):
        character_list = []
        for game_row in self.grid.values():
            character_list.extend(game_row.getEntities())
        return character_list
    
    def getAliveCharacterList(self):
        alive_list = []
        for game_row in self.grid.values():
            for entity in game_row.getEntities():
                if isinstance(entity, Character) and entity.isAlive():
                    alive_list.append(entity)
        return alive_list
    
    def getHateValue(self) -> list:
        hate_values = [row.getHateValue() for row in list(self.grid.values())[:3]]
        return hate_values
    
    def getCharacterByPosition(self, position: tuple) -> Character | None:
        row_name, pos_idx = position
        if row_name in self.grid:
            return self.grid[row_name].getCharacterByPosition(pos_idx)
        else:
            return None
    
    def isAllDead(self) -> bool:
        for game_row in self.grid.values():
            if not game_row.isAllDead():
                return False
        return True
    
    @staticmethod
    def randomGrid(stage=(1, 1)):
        import random
        new_grid = GameGrid()
        positions = ["front", "middle", "back"]
        for pos in positions:
            num_chars = random.randint(0, 3)
            for _ in range(num_chars):
                char_id = random.randint(1, 10)  # Assuming character IDs range from 1 to 10
                char = Character.byId(char_id)
                new_grid.setCharacter(char, pos)
        return new_grid
    
class GameBoard:
    def __init__(self, red_group: GameGrid, blue_group: GameGrid):
        self.red_group = red_group
        self.blue_group = blue_group
    
    def getTeamById(self, team_id) -> GameGrid | None:
        if self.red_group.team_id == team_id:
            return "RED"
        elif self.blue_group.team_id == team_id:
            return "BLUE"
        else:
            return None
        
    def getCharacterList(self):
        character_list = self.red_group.getCharacterList() + self.blue_group.getCharacterList()
        return character_list
        
    def isBattleOver(self) -> bool:
        return self.red_group.isAllDead() or self.blue_group.isAllDead()
    
    def draw(self, draw_type="terminal", screen=None, position=(0, 0)):
        if draw_type == "terminal":
            self.blue_group.draw(draw_type, screen, position, reverse=True)
            print("=" * 50)
            print(" " * 8 + "↑ Team Blue   VS   Team Red ↓")
            print("=" * 50)
            self.red_group.draw(draw_type, screen, position)

    def getOtherTeam(self, char: Character) -> GameGrid | None:
        if self.red_group.team_id == char.getAttr("team_id"):
            return self.blue_group
        elif self.blue_group.team_id == char.getAttr("team_id"):
            return self.red_group
        else:
            return None

if __name__ == "__main__":
    gr = GameRow()
    ch1 = Character.byId(1)
    ch2 = Character.byId(2)
    gr.setCharacter(ch1, 1)
    gr.setCharacter(ch2, 2)
    gr.draw()
    print(gr.removeCharacterByPosition(1))
    gr.draw()