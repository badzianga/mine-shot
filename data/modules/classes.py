from random import randint
from math import sin, cos, radians

from pygame.image import load
from pygame.math import Vector2
from pygame.sprite import Group, Sprite
from pygame.surface import Surface
from pygame.transform import scale

from .constants import GRAVITY, SCREEN_SIZE, WHITE
from .texts import DamageText


class HealthBar:
    def __init__(self):
        self.health_border = scale(load("data/img/bars/HealthBar.png").convert_alpha(), (192, 36))
        self.health_bar = scale(load("data/img/bars/HealthBar2.png").convert_alpha(), (153, 21))
        self.size = self.health_bar.get_size()

    def draw(self, screen: Surface, health: int, max_health: int):
        # draw border
        screen.blit(self.health_border, (SCREEN_SIZE[0] - 200, 8))  # border
        # draw current health
        screen.blit(
            self.health_bar,
            (SCREEN_SIZE[0] - 164, 16),
            (0, 0, int(self.size[0] * (health / max_health)), self.size[1])  # width of the bar
        )


class ManaBar:
    def __init__(self):
        self.mana_border = scale(load("data/img/bars/ManaBar.png").convert_alpha(), (192, 36))
        self.mana_bar = scale(load("data/img/bars/ManaBar2.png").convert_alpha(), (153, 21))
        self.size = self.mana_bar.get_size()

    def draw(self, screen: Surface, mana: float, max_mana: int):
        # draw border
        screen.blit(self.mana_border, (SCREEN_SIZE[0] - 200, 48))  # border
        # draw current mana
        screen.blit(
            self.mana_bar,
            (SCREEN_SIZE[0] - 164, 56),
            (0, 0, int(self.size[0] * (mana / max_mana)), self.size[1])  # width of the bar
        )


class Bullet(Sprite):
    def __init__(self, position: tuple, moving_left: bool, speed: int, angle_deg: float, damage: tuple, image: Surface, bounces=1):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect(center=position)
        self.true_position = Vector2(position[0], position[1])
        self.bounces = bounces

        if moving_left:
            self.vector = Vector2(-speed * cos(radians(angle_deg)), speed * sin(radians(angle_deg)))

        else:
            self.vector = Vector2(speed * cos(radians(angle_deg)), speed * sin(radians(angle_deg)))

        self.damage = randint(damage[0], damage[1])

    def draw(self, screen: Surface, scroll: list):
        screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

    def update(self, screen: Surface, scroll: list,  tiles: set, enemies: Group, texts: Group):
        # update bullet x position
        self.true_position.x += self.vector.x
        self.rect.x = int(self.true_position.x)

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
                    return

        # update bullet y position
        self.true_position.y += self.vector.y
        self.rect.y = int(self.true_position.y)

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
                    return

        # check for collisions with enemies
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                score = enemy.get_damage(self.damage)
                texts.add(DamageText((randint(enemy.rect.left, enemy.rect.right), randint(enemy.rect.top - 16, enemy.rect.top + 16)), str(self.damage), WHITE))
                self.kill()
                return score

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
            i = 5
        elif amount < 15:
            i = 10
        elif amount < 35:
            i = 25
        else:
            i = 50
        self.image = load(f"data/img/gold/{i}.png").convert_alpha()
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
