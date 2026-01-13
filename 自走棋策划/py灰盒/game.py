from util import *
from entity import Character, Entity
from grid import GameRow, GameGrid, GameBoard

class ShopEntity:

    def __init__(self):
        pass

class ShopRow(GameRow):

    def __init__(self, max_length=6):
        super().__init__(max_length=max_length)
        self.locked = [False] * self.max_length
        
    def isLocked(self, idx):
        idx -= 1  # Convert to 0-based index
        if 0 <= idx < self.max_length:
            return self.locked[idx]
        else:
            return False
        
    def refresh(self):
        for i in range(self.max_length):
            if not self.locked[i]:
                if self.getCharacterByPosition(i + 1) is not None:
                    self.removeCharacterByPosition(i + 1)
                self.setCharacter(Character.randomCharacter(), i + 1)

class Shop:

    def __init__(self, owner=None):
        self.characters = ShopRow(6)
        self.grade = 0
        self.owner = owner

    def buy(self, idx):
        char = self.characters.getCharacterByPosition(idx)
        if isinstance(char, Character):
            if self.owner.getAttr("money") >= char.getAttr("info.price"):
                self.owner.setAttr("money", self.owner.getAttr("money") - char.getAttr("info.price"))
                self.characters.removeCharacterByPosition(idx)
                em.broadcast("shop.bought", player=self.owner, character=char)
                self.draw()
                return char
            else:
                em.broadcast("shop.buy_failed", player=self.owner, reason="insufficient_funds", character=char)
                return None
        else:
            em.broadcast("shop.buy_failed", player=self.owner, reason="no_character", character=None)
            return None

    def refresh(self):
        self.characters.refresh()
        em.broadcast("shop.refreshed", player=self.owner)
        self.draw()

    def upgrade(self):
        if self.owner.getAttr("money") >= 10:
            self.owner.setAttr("money", self.owner.getAttr("money") - 10)
            self.grade += 1
            em.broadcast("shop.upgraded", player=self.owner, new_grade=self.grade)
            return True
        else:
            em.broadcast("shop.upgrade_failed", player=self.owner, reason="insufficient_funds")
            return False

    def lock(self, idx):
        pass

    def unlock(self, idx):
        pass

    def lockAll(self):
        pass

    def unlockAll(self):
        pass

    def draw(self):
        self.characters.draw()

class Player(Entity):

    def __init__(self):
        super().__init__()
        self.addAttr("money", 0)
        self.addAttr("max.hp", 100)
        self.addAttr("current.hp", 100)

        self.characters = GameRow(max_length=10)
        self.shop = Shop(owner=self)
        self.team = GameGrid()
        pass

    def setAttr(self, key: str, value):
        before_value = super().getAttr(key)
        if before_value != value:
            super().setAttr(key, value)
            em.broadcast('onAttrChange', player=self, attr=key, before=before_value, after=value)

if __name__ == "__main__":
    player = Player()
    player.setAttr("money", 50)
    player.shop.refresh()
    player.shop.buy(1)
    player.shop.buy(4)
    player.shop.refresh()