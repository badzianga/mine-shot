from pygame.font import Font
from pygame.surface import Surface

from .constants import DARK_GRAY, LIGHT_PURPLE, SCREEN_SIZE, WHITE


class Menu:
    def __init__(self):
        # menu font
        self.font = Font("data/fonts/Pixellari.ttf", 48)

        # texts and their positions
        self.texts = ("Start Game", "Settings", "Credits", "Exit")
        self.positions = (
            (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2 + 64),
            (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2 + 128),
            (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2 + 192),
            (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2 + 256)
        )

        # highlighted menu option (by default - new game)
        self.highlighted = 0

        # pressed keys
        self.key_up = False
        self.key_down = False

    def draw(self, screen: Surface):
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
                self.highlighted = 3
            else:
                self.highlighted -= 1

        # or move highlight down
        elif self.key_down:
            self.key_down = False
            if self.highlighted == 3:
                self.highlighted = 0
            else:
                self.highlighted += 1


class SettingsMenu:
    def __init__(self, settings):
        # global settings
        self.settings = settings

        # menu font
        self.font = Font("data/fonts/Pixellari.ttf", 48)

        # texts and their positions
        self.texts = ("Fullscreen", "Music volume", "Sounds volume", "Reset progress")
        self.positions = (
            (SCREEN_SIZE[0] // 4, SCREEN_SIZE[1] // 4),
            (SCREEN_SIZE[0] // 4, SCREEN_SIZE[1] // 4 + 64),
            (SCREEN_SIZE[0] // 4, SCREEN_SIZE[1] // 4 + 128),
            (SCREEN_SIZE[0] // 4, SCREEN_SIZE[1] // 4 + 192)
        )

        # highlighted menu option
        self.highlighted = 0

        # pressed keys
        self.key_up = False
        self.key_down = False

    def draw(self, screen: Surface):
        # settings buttons
        for i, text in enumerate(self.texts):
            if i == self.highlighted:
                text_surface = self.font.render(text, True, LIGHT_PURPLE)
            else:
                text_surface = self.font.render(text, True, WHITE)
            text_rect = text_surface.get_rect(topleft=self.positions[i])
            screen.blit(text_surface, text_rect)

        # settings values
        for i, value in enumerate(self.settings.values()):
            if i == self.highlighted:
                color = LIGHT_PURPLE
            else:
                color = WHITE
            if str(value).isdigit():
                    text = str(value) + '%'
            else:
                if value:
                    text = "On"
                else:
                    text = "Off"
            text_surface = self.font.render(text, True, color)
            text_rect = text_surface.get_rect(topright=(SCREEN_SIZE[0] - self.positions[i][0], self.positions[i][1]))
            screen.blit(text_surface, text_rect)

        # return button
        if self.highlighted == 4:
            text_surface = self.font.render("Return", True, LIGHT_PURPLE)
        else:
            text_surface = self.font.render("Return", True, WHITE)
        text_rect = text_surface.get_rect(center=(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] - 100))
        screen.blit(text_surface, text_rect)

    def update(self):
        # move highlight up
        if self.key_up:
            self.key_up = False
            if self.highlighted == 0:
                self.highlighted = 4
            else:
                self.highlighted -= 1

        # or move highlight down
        elif self.key_down:
            self.key_down = False
            if self.highlighted == 4:
                self.highlighted = 0
            else:
                self.highlighted += 1


class PauseMenu:
    def __init__(self):
        self.menu_rect = Surface((480, 244))
        self.menu_position = self.menu_rect.get_rect(center=(SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2))

        # menu font
        self.font = Font("data/fonts/Pixellari.ttf", 48)

        # texts and positions
        self.texts = ("Back to Game", "Settings", "Quit to Title")
        self.positions = (
            (self.menu_rect.get_width() // 2, 64),
            (self.menu_rect.get_width() // 2, 128),
            (self.menu_rect.get_width() // 2, 192)
        )

        # highlighted menu option
        self.highlighted = 0

        # pressed keys
        self.key_up = False
        self.key_down = False

    def draw(self, screen: Surface):
        self.menu_rect.fill(DARK_GRAY)
        for i, text in enumerate(self.texts):
            if i == self.highlighted:
                text_surface = self.font.render(text, True, LIGHT_PURPLE)
            else:
                text_surface = self.font.render(text, True, WHITE)
            text_rect = text_surface.get_rect(center=self.positions[i])
            self.menu_rect.blit(text_surface, text_rect)
        screen.blit(self.menu_rect, self.menu_position)

    def update(self):
        # move highlight up
        if self.key_up:
            self.key_up = False
            if self.highlighted == 0:
                self.highlighted = 2
            else:
                self.highlighted -= 1

        # or move highlight down
        elif self.key_down:
            self.key_down = False
            if self.highlighted == 2:
                self.highlighted = 0
            else:
                self.highlighted += 1
