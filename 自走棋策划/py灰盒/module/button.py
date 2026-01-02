import pygame

class ImageButton(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, image_path, image_hover_path=None, on_click=None):
        super().__init__()
        self.image_normal = pygame.transform.smoothscale(pygame.image.load(image_path).convert_alpha(), (w, h))
        self.image_hover = pygame.transform.smoothscale(pygame.image.load(image_hover_path).convert_alpha(), (w, h))
        self.image = self.image_normal
        self.rect = self.image.get_rect(topleft=(x, y))
        self.clicked = False
        self.on_click = on_click

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.image = self.image_hover
            if pygame.mouse.get_pressed()[0]:
                self.clicked = True
            elif self.clicked:
                self.clicked = False
                if self.on_click:
                    self.on_click()
        else:
            self.image = self.image_normal

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class TextButton(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, text, font_path, font_size, text_color, bg_color,
                 on_click=None, location='center', border_color=(80, 80, 80), border_width=0, border_radius=0):
        super().__init__()
        self.font = pygame.font.Font(font_path, font_size)
        self.text = text
        self.text_color = text_color
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width
        self.border_radius = border_radius
        self.on_click = on_click
        self.hovered = False
        self.clicked = False

        self.image = pygame.Surface((w, h), pygame.SRCALPHA)  # 用透明层支持圆角
        match location:
            case "topleft":
                self.rect = self.image.get_rect(topleft=(x, y))
            case "topright":
                self.rect = self.image.get_rect(topright=(x, y))
            case "midtop":
                self.rect = self.image.get_rect(midtop=(x, y))
            case "midbottom":
                self.rect = self.image.get_rect(midbottom=(x, y))
            case "center":
                self.rect = self.image.get_rect(center=(x, y))
            case _:
                raise ValueError("Invalid location argument")
        self.render()

    def render(self):
        w, h = self.image.get_size()
        self.image.fill((0, 0, 0, 0))  # 清空原图（透明）

        # 背景颜色（hover 时变暗）
        bg = tuple(max(0, c - 30) for c in self.bg_color) if self.hovered else self.bg_color
        pygame.draw.rect(self.image, bg, (0, 0, w, h), border_radius=self.border_radius)

        # 边框
        if self.border_width > 0:
            pygame.draw.rect(self.image, self.border_color, (0, 0, w, h),
                             width=self.border_width, border_radius=self.border_radius)

        # 文字
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(w // 2, h // 2))
        self.image.blit(text_surface, text_rect)

    def update(self, mouse_pos):
        was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)

        if self.hovered:
            if pygame.mouse.get_pressed()[0]:
                self.clicked = True
            elif self.clicked:
                self.clicked = False
                if self.on_click:
                    self.on_click()

        if self.hovered != was_hovered:
            self.render()

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)
