from random import randint

from pygame.font import Font
from pygame.image import load
from pygame.math import Vector2
from pygame.sprite import Group, Sprite
from pygame.surface import Surface
from pygame.transform import scale2x

from .constants import GOLD, GRAVITY, LIGHT_PURPLE, SCREEN_SIZE, WHITE
from .texts import DamageText


class HealthBar:
    def __init__(self):
        self.health_border = scale2x(load("data/img/bars/bar_border.png").convert_alpha())
        self.empty_bar = scale2x(load("data/img/bars/empty_bar.png").convert_alpha())
        self.health_bar = scale2x(load("data/img/bars/health_bar.png").convert_alpha())
        self.size = self.health_bar.get_size()

    def draw(self, screen: Surface, health: int, max_health: int):
        # draw border
        screen.blit(self.health_border, (SCREEN_SIZE[0] - 185, 18))  # border
        screen.blit(self.empty_bar, (SCREEN_SIZE[0] - 181, 20))
        # draw current health
        screen.blit(
            self.health_bar,
            (SCREEN_SIZE[0] - 181, 20),
            (0, 0, int(self.size[0] * (health / max_health)), self.size[1])  # width of the bar
        )


class ManaBar:
    def __init__(self):
        self.mana_border = scale2x(load("data/img/bars/bar_border.png").convert_alpha())
        self.empty_bar = scale2x(load("data/img/bars/empty_bar.png").convert_alpha())
        self.mana_bar = scale2x(load("data/img/bars/mana_bar.png").convert_alpha())
        self.size = self.mana_bar.get_size()

    def draw(self, screen: Surface, mana: float, max_mana: int):
        # draw border
        screen.blit(self.mana_border, (SCREEN_SIZE[0] - 185, 48))  # border
        screen.blit(self.empty_bar, (SCREEN_SIZE[0] - 181, 50))
        # draw current mana
        screen.blit(
            self.mana_bar,
            (SCREEN_SIZE[0] - 181, 50),
            (0, 0, int(self.size[0] * (mana / max_mana)), self.size[1])  # width of the bar
        )


class Menu:
    def __init__(self):
        # menu font
        self.font = Font("data/fonts/Pixellari.ttf", 48)

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


class Bullet(Sprite):
    def __init__(self, position: tuple, moving_left: bool, speeds: tuple, damage: tuple, image: Surface):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect(center=position)
        self.bounces = 1

        if moving_left:
            self.vector = Vector2(-speeds[0], speeds[1])

        else:
            self.vector = Vector2(speeds[0], speeds[1])

        self.damage = randint(damage[0], damage[1])

    def draw(self, screen: Surface, scroll: list):
        screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

    def update(self, screen: Surface, scroll: list,  tiles: set, enemies: Group, texts: Group):
        # update bullet x position
        self.rect.x += self.vector.x

        # check for x collisions with tiles
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.bounces > 0:
                    if self.vector.x > 0:
                        self.rect.right = tile.rect.left
                    else:
                        self.rect.left = tile.rect.right
                    self.vector.x *= -1
                    self.bounces -= 1
                    break
                else:
                    self.kill()

        # update bullet y position
        self.rect.y += self.vector.y

        # check for y collisions with tiles
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.bounces > 0:
                    if self.vector.y > 0:
                        self.rect.bottom = tile.rect.top
                    else:
                        self.rect.top = tile.rect.bottom
                    self.vector.y *= -1
                    self.bounces -= 1
                else:
                    self.kill()

        # check for collisions with enemies
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                enemy.get_damage(self.damage)
                texts.add(DamageText((randint(enemy.rect.left, enemy.rect.right), randint(enemy.rect.top - 16, enemy.rect.top + 16)), str(self.damage), WHITE))
                self.kill()

        # draw bullet
        self.draw(screen, scroll)


class Gold(Sprite):
    def __init__(self, position: tuple, amount: int):
        super().__init__()
        self.amount = amount
        if amount == 1:
            i = 1
        elif amount < 4:
            i = 2
        elif amount < 8:
            i = 4
        elif amount < 16:
            i = 8
        elif amount < 32:
            i = 16
        else:
            i = 32
        self.image = scale2x(load(f"data/img/gold/{i}.png").convert_alpha())
        self.rect = self.image.get_rect(midbottom=position)
        self.vel_y = 0

    def check_vertical_collisions(self, tiles: set):
        for tile in tiles:
            if tile.rect.colliderect(self.rect): 
                self.rect.bottom = tile.rect.top
                self.vel_y = 0
                break

    def draw(self, screen: Surface, scroll: list):
        screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

    def update(self, screen: Surface, scroll: list, tiles: set):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        self.check_vertical_collisions(tiles)

        self.draw(screen, scroll)
