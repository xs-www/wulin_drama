import pygame

class MainMenu:
    def __init__(self, screen: pygame.Surface, buttons: list):
        self.screen = screen
        self.buttons = buttons

    def update(self, mouse_pos):
        for button in self.buttons:
            button.update(mouse_pos)

    def draw(self):
        for button in self.buttons:
            button.draw(self.screen)