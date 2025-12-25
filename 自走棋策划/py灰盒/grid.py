from character import Character, BattleCharacter
import uuid

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

class GameGrid:
    def __init__(self, team_id=None):
        self.team_id = team_id if team_id is not None else uuid.uuid4()
        self.grid = {
            "front": GameRow(1),
            "middle": GameRow(2),
            "back": GameRow(3),
            "bench": GameRow(4)
        }


    def printGrid(self, reverse=False):
        rows = list(self.grid.items())
        if reverse:
            rows.reverse()
        for row_name, game_row in rows:
            print(f"{row_name.capitalize().ljust(6, ' ')} Row:", end=" | ")
            for entity_idx in range(game_row.max_length):
                if entity_idx < len(game_row.entities):
                    if game_row.entities[entity_idx]:
                        print(game_row.entities[entity_idx], end=" ")
                    else:
                        print(" " * 9, end=" ")
                else:
                    print(" " * 9, end=" ")
            print("|")

    def setCharacter(self, character: Character, row: str, idx: int = -1):
        if row in self.grid:
            if self.grid[row].setCharacter(character, idx):
                position = (row, self.grid[row].getPosition(character)[1])
                character.setPosition(position)
                character.setTeamId(self.team_id)
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
                if isinstance(entity, BattleCharacter) and entity.isAlive():
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
        
    def inBattleCopy(self) -> 'GameGrid':
        new_grid = GameGrid(self.team_id)
        for row_name, game_row in self.grid.items():
            for entity in game_row.getEntities():
                battle_Char = BattleCharacter(entity)
                new_grid.setCharacter(battle_Char, row_name)
        return new_grid
    
    def isAllDead(self) -> bool:
        for game_row in self.grid.values():
            for entity in game_row.getEntities():
                if isinstance(entity, BattleCharacter) and entity.alive:
                    return False
        return True
    
class GameBoard:
    def __init__(self, red_group: GameGrid, blue_group: GameGrid):
        self.red_group = red_group.inBattleCopy()
        self.blue_group = blue_group.inBattleCopy()

    def printBoard(self):
        self.blue_group.printGrid(reverse=True)
        print("-" * 50)
        self.red_group.printGrid()
    
    def getTeamById(self, team_id) -> GameGrid | None:
        if self.red_group.team_id == team_id:
            return "RED"
        elif self.blue_group.team_id == team_id:
            return "BLUE"
        else:
            return None
        
    def isBattleOver(self) -> bool:
        return self.red_group.isAllDead() or self.blue_group.isAllDead()
        
if __name__ == "__main__":
    red_group = GameGrid()
    blue_group = GameGrid()
    board = GameBoard(red_group, blue_group)
    board.printBoard()