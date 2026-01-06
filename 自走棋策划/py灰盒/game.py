from util import *
from entity import Character
from grid import GameRow, GameGrid, GameBoard

class Shop:

    def __init__(self):
        self.characters = []
        self.grade = 0
        self.owner = None
        pass

    def buy(self, idx):
        pass

    def refresh(self):
        pass

    def upgrade(self):
        pass

    def lock(self, idx):
        pass

    def unlock(self, idx):
        pass

    def lockAll(self):
        pass

    def unlockAll(self):
        pass

class Player:

    def __init__(self):
        self.money = 0
        self.characters = []
        self.shop = Shop()
        self.team = GameGrid()
        pass
