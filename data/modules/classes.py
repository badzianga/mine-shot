import pygame

from .constants import LIGHT_PURPLE, SCREEN_SIZE, WHITE


class HealthBar:
    def __init__(self):
        self.health_border = pygame.transform.scale2x(pygame.image.load("data/img/health_border.png").convert_alpha())
        self.health_bar = pygame.transform.scale2x(pygame.image.load("data/img/health_bar.png").convert_alpha())
        self.size = self.health_bar.get_size()

    def draw(self, screen, health, max_health):
        # draw border
        screen.blit(self.health_border, (SCREEN_SIZE[0] - 185, 18))  # border
        # draw current health
        screen.blit(
            self.health_bar,
            (SCREEN_SIZE[0] - 181, 20),
            (0, 0, int(self.size[0] * (health / max_health)), self.size[1])  # width of the bar
        )


class Menu:
    def __init__(self):
        # menu font
        self.font = pygame.font.Font("data/fonts/Pixellari.ttf", 48)

        # texts and positions
        self.texts = ("New Game", "Exit")
        self.positions = (
            (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2 + 64),
            (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2 + 128),
        )

        # highlighted menu option (by default - new game)
        self.highlighted = 0

        # pressed keys
        self.key_up = False
        self.key_down = False

    def draw(self, screen):
        for i, text in enumerate(self.texts):
            if i == self.highlighted:
                text_surface = self.font.render(text, True, LIGHT_PURPLE)
            else:
                text_surface = self.font.render(text, True, WHITE)
            text_rect = text_surface.get_rect(center=self.positions[i])
            screen.blit(text_surface, text_rect)

    def update(self):
        # move highlight up
        if self.key_up:
            self.key_up = False
            if self.highlighted == 0:
                self.highlighted = 1
            else:
                self.highlighted -= 1

        # or move highlight down
        elif self.key_down:
            self.key_down = False
            if self.highlighted == 1:
                self.highlighted = 0
            else:
                self.highlighted += 1
