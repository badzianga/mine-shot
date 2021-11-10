from math import sin
from random import choice, randint

from pygame.math import Vector2
from pygame.rect import Rect
from pygame.sprite import Group, Sprite, spritecollideany
from pygame.surface import Surface
from pygame.time import get_ticks

from .constants import BLUE, BROWN, GRAVITY, RED, TILE_SIZE, CHUNK_SIZE


class Player(Sprite):
    def __init__(self, position: tuple):
        super().__init__()

        # image - temporarily just a single-color surface
        self.image = Surface((TILE_SIZE // 2, TILE_SIZE - 8))
        self.image.fill(BLUE)
        self.flip = False

        # collision rect
        self.rect = self.image.get_rect(topleft=position)

        # movement stuff
        self.speed = 8
        self.vector = Vector2(0, 0)  # direction of movement
        self.jump_speed = -18
        self.on_ground = False
        self.climbing = False

        # health stuff
        self.max_health = 20
        self.health = 20
        self.invincible = False
        self.invincibility_duration = 90  # frames
        self.debuffs = {"burning": 0}  # debuff name: amount of get_damage to get

        # shooting
        self.shoot_cooldown = 0
        self.damage = (3, 5)

        # pressed keys
        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.jump = False

    def shoot(self, bullet_group: Group):
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = 45
            bullet_group.add(Bullet((self.rect.right, self.rect.centery), self.flip, self.damage))       

    def get_damage(self, damage: int):
        self.health -= damage
        self.invincible = True

    def check_ladder_collisions(self, ladders: Group):
        ladder_collision = False
        
        for ladder in ladders:
            if self.rect.colliderect(ladder.rect):
                ladder_collision = True

                # center player on the ladder
                if self.climbing:
                    self.vector.y = 0
                    self.rect.centerx = ladder.rect.centerx

                # go up
                if self.up:
                    self.vector.y -= self.speed * 0.75
                    if not self.climbing:
                        self.climbing = True

                # go down
                if self.down:
                    self.vector.y += self.speed * 0.75
                    if not self.climbing:
                        self.climbing = True

        # allow moving when on top of ladder
        if not ladder_collision:
            self.climbing = False

    def check_tile_collisions(self, scroll: list, game_map: dict):
        # update x position
        self.rect.x += self.vector.x

        # check horizontal collisions (x)
        for y in range(3):
            for x in range(4):
                target_x = x - 1 + round(scroll[0] / (CHUNK_SIZE * TILE_SIZE))
                target_y = y - 1 + round(scroll[1] / (CHUNK_SIZE * TILE_SIZE))
                target_chunk = f"{target_x};{target_y}"
                if target_chunk not in game_map.keys():
                    continue
                for tile in game_map[target_chunk]:
                    if tile.rect.colliderect(self.rect):
                        # touching right wall
                        if self.vector.x < 0:
                            self.rect.left = tile.rect.right
                            break
                        # touching left wall
                        elif self.vector.x > 0:
                            self.rect.right = tile.rect.left
                            break

        # update y position
        self.rect.y += self.vector.y

        # check vertical collisions (y)
        for y in range(3):
            for x in range(4):
                target_x = x - 1 + round(scroll[0] / (CHUNK_SIZE * TILE_SIZE))
                target_y = y - 1 + round(scroll[1] / (CHUNK_SIZE * TILE_SIZE))
                target_chunk = f"{target_x};{target_y}"
                if target_chunk not in game_map.keys():
                    continue
                for tile in game_map[target_chunk]:
                    if tile.rect.colliderect(self.rect):
                        # touching floor - stop falling, allow jump, stop climbing
                        if self.vector.y > 0:
                            self.vector.y = 0
                            self.rect.bottom = tile.rect.top
                            self.on_ground = True
                            self.climbing = False
                            break
                        # touching ceiling - start falling
                        elif self.vector.y < 0:
                            self.vector.y = 0
                            self.rect.top = tile.rect.bottom
                            break

        # if player is in air and collision didn't happen, disable jump
        # without it, when falling from a block, you can jump in air
        # > 1 because of gravitation
        if self.vector.y > 1:
            self.on_ground = False

    def check_platform_collisions(self, platforms: Group):
        collision_rect = Rect(self.rect.x, self.rect.y + TILE_SIZE - 1, self.rect.width, 1)
        # check 'feet' (collision_rect) colliding with platform
        for platform in platforms:
            if platform.rect.colliderect(collision_rect):
                # touching platform - stop falling, allow jump, stop climbing
                if self.vector.y > 0:
                    self.vector.y = 0
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                    self.climbing = False

                    # jump from the platform
                    if self.down and self.jump:
                        self.on_ground = False
                        self.vector.y += GRAVITY * 2

                    break

    def check_enemy_collisions(self, enemies: Group):
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                self.get_damage(randint(enemy.damage[0], enemy.damage[1]))
                break

    def check_lava_collisions(self, lava_tiles: Group):
        for lava_tile in lava_tiles:
            if self.rect.colliderect(lava_tile.rect):
                # slow player while in lava, allow to "swim" (jmup)
                self.speed = 2
                self.jump_speed = -9
                self.vector.y *= 0.3
                self.on_ground = True

                if not self.invincible:
                    # recieve damage from lava
                    self.get_damage(randint(lava_tile.damage[0], lava_tile.damage[1]))
                    # apply debuff
                    self.debuffs["burning"] = 3

                return

        self.speed = 8
        self.jump_speed = -18

    def update(self, screen: Surface, scroll: list, game_map: dict):
        # apply gravity
        self.vector.y += GRAVITY

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # check collisions and fix position
        self.check_tile_collisions(scroll, game_map)

        # move left
        if self.left and not self.climbing:
            self.vector.x = -self.speed
            self.flip = True
        # or move right
        elif self.right and not self.climbing:
            self.vector.x = self.speed
            self.flip = False
        # or stop moving
        else:
            self.vector.x = 0
        # jump (from ground or from ladder)
        if (self.jump and self.on_ground) or (self.jump and self.climbing):
            self.vector.y = self.jump_speed
            self.jump = False
            self.on_ground = False
            self.climbing = False

        # set max falling spedd - temp fix for bug with platform collision
        if self.vector.y > 18:
            self.vector.y = 18

        # update invincivbility
        if self.invincible:
            self.invincibility_duration -= 1
            if self.invincibility_duration <= 0:
                self.invincibility_duration = 90
                self.invincible = False

        # blinking if damaged
        if self.invincible:
            alpha = sin(get_ticks())
            if alpha >= 0:
                self.image.set_alpha(255)
            else:
                self.image.set_alpha(0)
        else:
            self.image.set_alpha(255)

        # draw player
        screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))


class Enemy(Sprite):
    def __init__(self, position: tuple):
        super().__init__()
        self.image = Surface((TILE_SIZE // 2, TILE_SIZE - 8))
        self.image.fill(RED)

        self.rect = self.image.get_rect(topleft=(position[0], position[1] + 8))

        self.health = 10

        self.speed = randint(3, 5)
        self.vel_y = 0
        self.damage = (1, 3)
        self.idling = False
        self.idling_counter = 0

    def check_tile_collisions(self, tiles: Group):
        # update x position
        self.rect.x += self.speed

        # check horizontal collisions (x)
        for tile in tiles:
            if tile.rect.colliderect(self.rect):
                # touching right wall
                if self.speed < 0:
                    self.rect.left = tile.rect.right
                    self.speed *= -1
                    break
                # touching left wall
                elif self.speed > 0:
                    self.rect.right = tile.rect.left
                    self.speed *= -1
                    break

        self.rect.y += self.vel_y

        # chech vertical collisions (y)
        for tile in tiles:
            if tile.rect.colliderect(self.rect):
                # touching floor - stop falling
                self.rect.bottom = tile.rect.top
                self.vel_y = 0
                break

    def update(self, screen: Surface, scroll: list, tiles: Group):
        # apply gravity
        self.vel_y += GRAVITY

        # update position and check collisions with tiles
        self.check_tile_collisions(tiles)

        if not self.idling:
            # random idle
            if randint(1, 200) == 1:
                self.idling = True
                self.idling_counter = randint(30, 70)

        else:
            self.idling_counter -= 1
            # after idle - stop idling, randomly select direction of moving
            if self.idling_counter <= 0:
                self.idling = False
                self.speed *= choice((-1, 1))

        # kill enemy is health below or equals 0
        if self.health <= 0:
            self.kill()

        # draw enemy on the screen
        screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))


class Bullet(Sprite):
    def __init__(self, position: tuple, moving_right: bool, damage: tuple):
        super().__init__()

        self.image = Surface((8, 8))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect(center=position)

        if moving_right:
            self.speed = -16
        else:
            self.speed = 16

        self.damage = randint(damage[0], damage[1])

    def draw(self, screen: Surface, scroll: list):
        screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

    def update(self, screen: Surface, scroll: list,  tiles: Group, enemies: Group):
        # update bullet position
        self.rect.x += self.speed

        # draw bullet
        self.draw(screen, scroll)

        # check for collisions with level
        if spritecollideany(self, tiles):
            self.kill()

        # check for collisions with enemies
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                enemy.health -= self.damage
                self.kill()
