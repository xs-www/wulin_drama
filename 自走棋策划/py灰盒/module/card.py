import pygame

class Card(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, text, font: pygame.font.Font,
                 text_color=(0, 0, 0), bg_color=(200, 200, 200),
                 border_color=(0, 0, 0), border_width=2,
                 border_radius=10, location="topleft", on_click=None):
        super().__init__()
        self.font = font

    def onUse(self, user, target, game_grid):
        pass