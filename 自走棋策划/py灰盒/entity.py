import pygame

class Entity(pygame.sprite.Sprite):

    def __init__(self, health_points=100, position=(0, 0)):
        super().__init__()
        self.health_points = health_points
        self.position = position

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

    