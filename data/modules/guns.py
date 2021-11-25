from random import randint, random
from pygame import Vector2

from pygame.image import load
from pygame.rect import Rect
from pygame.sprite import Group
from pygame.transform import scale2x

from .classes import Bullet


class Shotgun:
    def __init__(self, bullet_group: Group, player_vector: Vector2):
        self.damage = (1, 5)
        self.cooldown = 0
        self.max_cooldowns = [45, 60]

        self.bullet_group = bullet_group
        self.player_vector = player_vector
        self.bullet_img = load("data/img/bullet.png").convert_alpha()

    def shoot(self, player_rect: Rect, player_flip: bool, key_up: bool, key_down: bool):
        if self.cooldown <= 0:
            self.cooldown = self.max_cooldowns[0]
            if key_up:
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 20, -55, self.damage, self.bullet_img))
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 20, -60, self.damage, self.bullet_img))
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 20, -65, self.damage, self.bullet_img))
            elif key_down:
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 20, 55, self.damage, self.bullet_img))
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 20, 60, self.damage, self.bullet_img))
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 20, 65, self.damage, self.bullet_img))
            else:
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 20, 5, self.damage, self.bullet_img))
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 20, 0, self.damage, self.bullet_img))
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 20, -5, self.damage, self.bullet_img))

    def special(self, player_rect: Rect, player_flip: bool, player_mana: float, key_up: bool, key_down: bool):
        if self.cooldown <= 0 and player_mana >= 40:
            player_mana -= 40
            self.cooldown = self.max_cooldowns[1]
            if key_up:
                for _ in range(8):
                    self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, randint(16, 20), randint(-100, -80), self.damage, self.bullet_img))
            elif key_down:
                for _ in range(8):
                    self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, randint(16, 20), randint(80, 100), self.damage, self.bullet_img))
                if self.player_vector.y < 0:
                    self.player_vector.y = self.player_vector.y * 2.25
                else:
                    self.player_vector.y = -13
            else:
                for _ in range(8):
                    self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, randint(16, 20), randint(-10, 10), self.damage, self.bullet_img))

        return player_mana


class Handgun:
    def __init__(self, bullet_group: Group, player_vector: Vector2):
        self.damage = (1, 3)
        self.cooldown = 0
        self.max_cooldowns = [40, 15]

        self.bullet_group = bullet_group
        self.player_vector = player_vector
        self.bullet_img = load("data/img/bullet.png").convert_alpha()

    def shoot(self, player_rect: Rect, player_flip: bool, key_up: bool, key_down: bool):
        if self.cooldown <= 0:
            self.cooldown = self.max_cooldowns[0]
            if key_up:
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 20, -62 + random() * 4, self.damage, self.bullet_img))
            elif key_down:
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 20, 58 + random() * 4, self.damage, self.bullet_img))
            else:
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 20, -2 + random() * 4, self.damage, self.bullet_img))

    def special(self, player_rect: Rect, player_flip: bool, player_mana: float, key_up: bool, key_down: bool):
        if self.cooldown <= 0 and player_mana >= 20:
            player_mana -= 20
            self.cooldown = self.max_cooldowns[1]
            if key_up:
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, randint(18, 24), -64 + random() * 8, self.damage, self.bullet_img, 2))
            elif key_down:
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, randint(18, 24), 56 + random() * 8, self.damage, self.bullet_img, 2))
            else:
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, randint(18, 24), -4 + random() * 8, self.damage, self.bullet_img, 2))

        return player_mana


class BigShot:
    def __init__(self, bullet_group: Group, player_vector: Vector2):
        self.damage = (8, 15)
        self.cooldown = 0
        self.max_cooldowns = [60, 120]

        self.bullet_group = bullet_group
        self.player_vector = player_vector
        self.bullet_img = load("data/img/bullet.png").convert_alpha()
        self.bullet_img2 = scale2x(load("data/img/bullet.png").convert_alpha())

    def shoot(self, player_rect: Rect, player_flip: bool, key_up: bool, key_down: bool):
        if self.cooldown <= 0:
            self.cooldown = self.max_cooldowns[0]
            if key_up:
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 30, -60, self.damage, self.bullet_img))
            elif key_down:
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 30, 60, self.damage, self.bullet_img))
            else:
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 30, 0, self.damage, self.bullet_img))

    def special(self, player_rect: Rect, player_flip: bool, player_mana: float, key_up: bool, key_down: bool):
        if self.cooldown <= 0 and player_mana >= 50:
            player_mana -= 50
            self.cooldown = self.max_cooldowns[1]
            if key_up:
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 25, -60, self.damage, self.bullet_img2, 5))
            elif key_down:
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 25, 60, self.damage, self.bullet_img2, 5))
            else:
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 25, 0, self.damage, self.bullet_img2, 5))

        return player_mana


class Minigun:
    def __init__(self, bullet_group: Group, player_vector: Vector2):
        self.damage = (1, 2)
        self.cooldown = 0
        self.max_cooldowns = [10, 10]

        self.bullet_group = bullet_group
        self.player_vector = player_vector
        self.bullet_img = load("data/img/bullet.png").convert_alpha()

    def shoot(self, player_rect: Rect, player_flip: bool, key_up: bool, key_down: bool):
        if self.cooldown <= 0:
            self.cooldown = self.max_cooldowns[0]
            if key_up:
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 25, -70 + random() * 20, self.damage, self.bullet_img, 0))
            elif key_down:
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 25, 50 + random() * 20, self.damage, self.bullet_img, 0))
            else:
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 25, -10 + random() * 20, self.damage, self.bullet_img, 0))

    def special(self, player_rect: Rect, player_flip: bool, player_mana: float, key_up: bool, key_down: bool):
        if self.cooldown <= 0 and player_mana >= 15:
            player_mana -= 15
            self.cooldown = self.max_cooldowns[1]
            if key_up:
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 25, -70 + random() * 20, self.damage, self.bullet_img))
            elif key_down:
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 25, 50 + random() * 20, self.damage, self.bullet_img))
            else:
                self.bullet_group.add(Bullet((player_rect.centerx, player_rect.centery), player_flip, 25, -10 + random() * 20, self.damage, self.bullet_img))

        return player_mana
