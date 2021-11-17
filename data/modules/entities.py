from math import cos, radians, sin
from random import choice, randint

from pygame.image import load
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.sprite import Group, Sprite
from pygame.surface import Surface
# from pygame.draw import rect as draw_rect
from pygame.time import get_ticks

from .classes import Bullet, Gold
from .constants import BLACK, BLUE, GOLD, GRAVITY, GREEN, ORANGE, RED, TILE_SIZE
from .texts import DamageText


class Player(Sprite):
    def __init__(self, position: tuple):
        super().__init__()

        # image - temporarily just a single-color surface
        self.image = Surface((TILE_SIZE // 2, TILE_SIZE - 8))
        self.image.fill(BLUE)
        self.flip = False
        self.bullet_img = load("data/img/bullet.png").convert_alpha()

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
        self.max_mana = 100
        self.mana = 100
        self.invincible = False
        self.invincibility_duration = 90  # frames
        self.debuffs = {"burning": 0, "poison": 0}  # debuff name: amount of get_damage to get

        # shooting
        self.shoot_cooldown = 0
        self.damage = (1, 5)

        # pressed keys
        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.jump = False

        self.gold = 0

    def get_damage(self, damage: int, texts: Group):
        self.health -= damage
        if self.debuffs["burning"] > 0:
            color = ORANGE
        elif self.debuffs["poison"] > 0:
            color = GREEN
        else:
            color = RED
        texts.add(DamageText((randint(self.rect.left, self.rect.right), randint(self.rect.top - 8, self.rect.top + 8)), str(damage), color))
        self.invincible = True

    def shoot(self, bullet_group: Group):
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = 45
            if self.up:
                bullet_group.add(Bullet((self.rect.centerx, self.rect.centery), self.flip, 20, -55, self.damage, self.bullet_img))
                bullet_group.add(Bullet((self.rect.centerx, self.rect.centery), self.flip, 20, -60, self.damage, self.bullet_img))
                bullet_group.add(Bullet((self.rect.centerx, self.rect.centery), self.flip, 20, -65, self.damage, self.bullet_img))
            elif self.down:
                bullet_group.add(Bullet((self.rect.centerx, self.rect.centery), self.flip, 20, 55, self.damage, self.bullet_img))
                bullet_group.add(Bullet((self.rect.centerx, self.rect.centery), self.flip, 20, 60, self.damage, self.bullet_img))
                bullet_group.add(Bullet((self.rect.centerx, self.rect.centery), self.flip, 20, 65, self.damage, self.bullet_img))
            else:
                bullet_group.add(Bullet((self.rect.centerx, self.rect.centery), self.flip, 20, 5, self.damage, self.bullet_img))
                bullet_group.add(Bullet((self.rect.centerx, self.rect.centery), self.flip, 20, 0, self.damage, self.bullet_img))
                bullet_group.add(Bullet((self.rect.centerx, self.rect.centery), self.flip, 20, -5, self.damage, self.bullet_img))

    def burst(self, bullet_group: Group):
        if self.shoot_cooldown <= 0 and self.mana >= 40:
            self.mana -= 40
            self.shoot_cooldown = 60
            if self.up:
                for _ in range(8):
                    bullet_group.add(Bullet((self.rect.centerx, self.rect.centery), self.flip, randint(16, 20), randint(-100, -80), self.damage, self.bullet_img))
            elif self.down:
                for _ in range(8):
                    bullet_group.add(Bullet((self.rect.centerx, self.rect.centery), self.flip, randint(16, 20), randint(80, 100), self.damage, self.bullet_img))
            else:
                for _ in range(8):
                    bullet_group.add(Bullet((self.rect.centerx, self.rect.centery), self.flip, randint(16, 20), randint(-10, 10), self.damage, self.bullet_img))

    def check_horizontal_collisions(self, tiles: set):
        for tile in tiles:
            if tile.rect.colliderect(self.rect):
                # touching right wall
                if self.vector.x < 0:
                    self.rect.left = tile.rect.right
                    return  # finish looking for collisions
                # touching left wall
                elif self.vector.x > 0:
                    self.rect.right = tile.rect.left
                    return  # finish looking for collisions

    def check_vertical_collisions(self, tiles: set):
        for tile in tiles:
            if tile.rect.colliderect(self.rect):
                # touching floor - stop falling, allow jump, stop climbing
                if self.vector.y > 0:
                    self.vector.y = 0
                    self.rect.bottom = tile.rect.top
                    self.on_ground = True
                    self.climbing = False
                    return  # finish looking for collisions
                # touching ceiling - start falling
                elif self.vector.y < 0:
                    self.vector.y = 0
                    self.rect.top = tile.rect.bottom
                    return  # finish looking for collisions

        # if player is in air and collision didn't happen, disable jump
        # without it, when falling from a block, you can jump in air
        if self.vector.y > 1:
            self.on_ground = False

    def check_ladder_collisions(self, ladders: set):
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

    def check_platform_collisions(self, platforms: set):
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

    def check_lava_collisions(self, lava_tiles: set, texts: Group):
        for lava_tile in lava_tiles:
            if self.rect.colliderect(lava_tile.rect):
                # slow player while in lava, allow to "swim" (jmup)
                self.speed = 2
                self.jump_speed = -9
                self.vector.y *= 0.3
                self.on_ground = True

                if not self.invincible:
                    # recieve damage from lava
                    self.get_damage(randint(lava_tile.damage[0], lava_tile.damage[1]), texts)
                    # apply debuff
                    self.debuffs["burning"] = 3

                return

        # restore speed values if not in lava
        self.speed = 8
        self.jump_speed = -18

    def check_enemy_collisions(self, enemies: Group, texts: Group):
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                damage = randint(enemy.damage[0], enemy.damage[1])
                self.get_damage(damage, texts)
                break

    def check_coins_collisions(self, gold_group: Group, texts: Group):
        for gold in gold_group:
            if self.rect.colliderect(gold.rect):
                self.gold += gold.amount
                texts.add(DamageText(self.rect.midtop, f"{gold.amount}$", GOLD))
                gold.kill()

    def draw(self, screen: Surface, scroll: set):
        screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

    def update(self, screen: Surface, scroll: list, objects: dict, enemies: Group, texts: Group, gold_group: Group):
        # update x position and check for horizontal collisions
        self.rect.x += self.vector.x
        self.check_horizontal_collisions(objects["tiles"])
        
        # update y position and check for verical collisions
        self.vector.y += GRAVITY
        self.rect.y += self.vector.y
        self.check_vertical_collisions(objects["tiles"])

        # check for collisions with other objects (except enemies)
        self.check_ladder_collisions(objects["ladders"])
        self.check_platform_collisions(objects["platforms"])
        self.check_lava_collisions(objects["lava"], texts)
        self.check_coins_collisions(gold_group, texts)

        # update shoot cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # regenerate mana
        if self.mana < 100:
            self.mana += 0.1

        # move left
        if self.left:
            if not self.climbing:
                self.vector.x = -self.speed
            self.flip = True
        # or move right
        elif self.right:
            if not self.climbing:
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

        # set max falling speed
        if self.vector.y > 18:
            self.vector.y = 18

        # check for collisions with enemies
        if not self.invincible:
            self.check_enemy_collisions(enemies, texts)
            # get damage from debuffs
            if self.debuffs["burning"] > 0:
                self.get_damage(2, texts)
                self.debuffs["burning"] -= 1

        # update invincivbility
        if self.invincible:
            self.invincibility_duration -= 1
            if self.invincibility_duration <= 0:
                self.invincibility_duration = 90
                self.invincible = False

        # blinking if damaged
        if self.invincible:
            if sin(get_ticks()) >= 0:
                self.image.set_alpha(255)
            else:
                self.image.set_alpha(63)
        else:
            self.image.set_alpha(255)

        # draw player
        self.draw(screen, scroll)


class EnemyBase(Sprite):
    def __init__(self, position, hp, damage, speed, gold, gold_group):
        super().__init__()

        self.gold_group = gold_group

        # image and rect
        self.image = Surface((TILE_SIZE // 2, TILE_SIZE - 8))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(position[0], position[1]))

        # health, damage, speed and gold amount from config file
        if isinstance(hp, list):
            self.health = randint(hp[0], hp[1])
        else:
            self.health = hp

        self.damage = tuple(damage)

        if isinstance(speed, list):
            self.speed = randint(speed[0], speed[1])
        else:
            self.speed = speed

        if isinstance(gold, list):
            self.gold_amount = randint(gold[0], gold[1])
        else:
            self.gold_amount = gold

        self.blinking = 0  # blinking time after damaged

        self.vector = Vector2(0, 0)

        # current status and idle time
        self.idling = False
        self.idling_counter = 0

    def get_damage(self, damage: int):
        self.health -= damage
        self.blinking = 30
        if self.health <= 0:
            if self.gold_amount > 0:
                self.gold_group.add(Gold((randint(self.rect.left, self.rect.right), self.rect.bottom), self.gold_amount))
            self.kill()
            return

    def draw(self, screen: Surface, scroll: list):
        screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

    def check_horizontal_collisions(self, tiles: set):
        for tile in tiles:
            if tile.rect.colliderect(self.rect):
                # touching right wall
                if self.vector.x < 0:
                    self.rect.left = tile.rect.right
                    self.vector.x *= -1
                    break
                # touching left wall
                elif self.vector.x > 0:
                    self.rect.right = tile.rect.left
                    self.vector.x *= -1
                    break

    def check_vertical_collisions(self, tiles: set):
        for tile in tiles:
            if tile.rect.colliderect(self.rect):
                # touching floor - stop falling
                self.rect.bottom = tile.rect.top
                self.vector.y = 0
                break


class Enemy0(EnemyBase):
    def __init__(self, position: tuple, hp, damage, speed, gold, gold_group):
        super().__init__(position, hp, damage, speed, gold, gold_group)
        self.image.fill(GREEN)

        self.vector.x = self.speed * choice((-1, 1))

    def update(self, screen: Surface, scroll: list, tiles: set, platforms: set, player_rect: Rect):
        if not self.idling:
            # update x position and check for horizontal collisions
            self.rect.x += self.vector.x
            self.check_horizontal_collisions(tiles)

            # random idle
            if randint(1, 200) == 1:
                self.idling = True
                self.idling_counter = randint(30, 70)
        else:
            self.idling_counter -= 1
            # after idle - stop idling, randomly select direction of moving
            if self.idling_counter <= 0:
                self.idling = False
                self.vector.x *= choice((-1, 1))

        # update y position and check collisions with tiles
        self.vector.y += GRAVITY
        self.rect.y += self.vector.y
        self.check_vertical_collisions(set.union(tiles, platforms))

        # set max falling spedd - temp fix for bug with platform collision
        if self.vector.y > 18:
            self.vector.y = 18

        # blinking if damaged
        if self.blinking:
            self.blinking -= 1
            if sin(get_ticks()) >= 0:
                self.image.set_alpha(255)
            else:
                self.image.set_alpha(63)
        else:
            self.image.set_alpha(255)

        # draw enemy on the screen
        self.draw(screen, scroll)


class Enemy1(EnemyBase):
    def __init__(self, position: tuple, hp, damage, speed, gold, gold_group):
        super().__init__(position, hp, damage, speed, gold, gold_group)
        self.image = Surface((32, 32))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect(topleft=position)
        self.vision_rect = Rect(0, 0, 640, 240)

    def update(self, screen: Surface, scroll: list, tiles: set, platforms: set, player_rect: Rect):
        if not self.idling:
            # random idle
            if randint(1, 50) == 1:
                self.idling = True
                self.idling_counter = randint(30, 70)
                
            # update x position and check for horizontal collisions
            self.rect.x += self.vector.x
            self.check_horizontal_collisions(tiles)
        else:
            self.idling_counter -= 1
            # after idle - stop idling, randomly select direction of moving
            if self.idling_counter <= 0:
                self.idling = False
                self.vector.x *= choice((-1, 1))

        # update y position and check collisions with tiles
        self.vector.y += GRAVITY
        self.rect.y += self.vector.y
        self.check_vertical_collisions(set.union(tiles, platforms))

        # set max falling spedd - temp fix for bug with platform collision
        if self.vector.y > 18:
            self.vector.y = 18

        # update enemy vision
        self.vision_rect.midbottom = self.rect.midbottom
        # if enemy "sees" the player
        if self.vision_rect.colliderect(player_rect):
            self.idling = False
            # change enemy direction to go after the player
            if player_rect.x < self.rect.x - 5:
                    self.vector.x = -self.speed
            elif player_rect.x > self.rect.x + 5:
                    self.vector.x = self.speed
            else:
                self.vector.x = 0
        elif self.vector.x == 0:
            self.vector.x = self.speed * choice((-1, 1))
        # TEMP: enemy vision
        # draw_rect(screen, GOLD, (self.vision_rect.left - scroll[0], self.vision_rect.top - scroll[1], self.vision_rect.width, self.vision_rect.height))

        # blinking if damaged
        if self.blinking:
            self.blinking -= 1
            if sin(get_ticks()) >= 0:
                self.image.set_alpha(255)
            else:
                self.image.set_alpha(63)
        else:
            self.image.set_alpha(255)

        # draw enemy on the screen
        self.draw(screen, scroll)


class Enemy2(EnemyBase):
    def __init__(self, position: tuple, hp, damage, speed, gold, gold_group):
        super().__init__(position, hp, damage, speed, gold, gold_group)

        self.image = Surface((48, 48))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect(topleft=position)

        self.vision_rect = Rect(0, 0, 640, 360)

        self.move_count = 30

    def check_horizontal_collisions(self, tiles: set):
        for tile in tiles:
            if tile.rect.colliderect(self.rect):
                # touching tile right wall
                if self.vector.x < 0:
                    self.rect.left = tile.rect.right
                    random_angle = randint(-90, 90)
                    self.vector.x = self.speed * cos(radians(random_angle))
                    self.vector.y = self.speed * sin(radians(random_angle))
                    break
                # touching tile left wall
                elif self.vector.x > 0:
                    self.rect.right = tile.rect.left
                    random_angle = randint(90, 270)
                    self.vector.x = self.speed * cos(radians(random_angle))
                    self.vector.y = self.speed * sin(radians(random_angle))
                    break

    def check_vertical_collisions(self, tiles: set):
        for tile in tiles:
            if tile.rect.colliderect(self.rect):
                # touching floor
                if self.vector.y > 0:
                    self.rect.bottom = tile.rect.top
                    random_angle = randint(180, 360)
                    self.vector.x = self.speed * cos(radians(random_angle))
                    self.vector.y = self.speed * sin(radians(random_angle))
                    break
                # touching ceiling
                elif self.vector.y < 0:
                    self.rect.top = tile.rect.bottom
                    random_angle = randint(0, 180)
                    self.vector.x = self.speed * cos(radians(random_angle))
                    self.vector.y = self.speed * sin(radians(random_angle))
                    break

    def update(self, screen: Surface, scroll: list, tiles: set, platforms: set, player_rect: Rect):
        if self.move_count == 0:
            random_angle = randint(1, 360)
            self.vector.x = self.speed * cos(radians(random_angle))
            self.vector.y = self.speed * sin(radians(random_angle))
            self.idling = True
            self.idling_counter = randint(30, 50)
            self.move_count = randint(30, 50)
        
        if self.idling:
            self.idling_counter -= 1
            if self.idling_counter <= 0:
                self.idling = False
        else:
            self.move_count -= 1   
            # update x position and check for horizontal collisions
            self.rect.x += self.vector.x
            self.check_horizontal_collisions(tiles)

            # update y position and check collisions with tiles
            self.rect.y += self.vector.y
            self.check_vertical_collisions(tiles)

        # # update enemy vision
        # self.vision_rect.center = self.rect.center
        # # if enemy "sees" the player
        # if self.vision_rect.colliderect(player_rect):
        #     self.idling = False
        #     # change enemy direction to go after the player
        #     if player_rect.x < self.rect.x - 5:
        #             # VECTOR CHANGE HERE
        #             pass
        #     elif player_rect.x > self.rect.x + 5:
        #             # VECTOR CHANGE HERE
        #             pass
        #     else:
        #         # VECTOR CHANGE HERE
        #         pass
        # elif self.vector.x == 0:
        #     # VECTOR CHANGE HERE?
        #     pass

        # blinking if damaged
        if self.blinking:
            self.blinking -= 1
            if sin(get_ticks()) >= 0:
                self.image.set_alpha(255)
            else:
                self.image.set_alpha(63)
        else:
            self.image.set_alpha(255)

        # draw enemy on the screen
        self.draw(screen, scroll)
