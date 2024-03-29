from math import atan2, cos, floor, radians, sin
from random import choice, randint

from pygame.math import Vector2
from pygame.rect import Rect
from pygame.sprite import Group, Sprite
from pygame.surface import Surface
from pygame.time import get_ticks
from pygame.transform import flip, smoothscale

from .classes import Gold
from .constants import GOLD, GRAVITY, GREEN, ORANGE, RED, TILE_SIZE
from .functions import load_images
from .guns import Handgun, Minigun, Shotgun
from .texts import DamageText


class Player(Sprite):
    def __init__(self, position: tuple, images: tuple, selected_gun: str, enemies: Group, gold_group: Group, bullet_group: Group, texts: Group, upgrades: list, gold: int, health: int, max_health: int):
        super().__init__()

        self.animations = {"idle": [], "run": [], "climb": images[2], "jump": []}
        for image in images[0]:
            self.animations["idle"].append(smoothscale(image, (image.get_width() * 1.5, image.get_height() * 1.5)))
        for image in images[1]:
            self.animations["run"].append(smoothscale(image, (image.get_width() * 1.5, image.get_height() * 1.5)))
        self.animations["idle"] = tuple(self.animations["idle"])
        self.animations["run"] = tuple(self.animations["run"])
        self.animations["jump"].append(smoothscale(images[3], (images[3].get_width() * 1.5, images[3].get_height() * 1.5)))
        self.frame_index = 0
        self.action = "idle"
        self.cooldowns = {"idle": 0.15, "run": 0.3, "climb": 0.2, "jump": 0.01}
        self.image = self.animations[self.action][self.frame_index]
        self.flip = False

        # collision rect
        self.rect = self.image.get_rect(midbottom=position)

        # movement stuff
        self.speed = 8
        self.vector = Vector2(0, 0)  # direction of movement
        self.jump_speed = -18
        self.on_ground = True
        self.climbing = False

        # health stuff
        self.max_health = max_health
        self.health = health
        self.max_mana = 100
        self.mana = self.max_mana
        self.mana_regen = 0.1
        self.invincible = False
        self.invincibility_duration = 90  # frames
        self.debuffs = {"burning": 0, "poison": 0}  # debuff name: amount of get_damage to get

        # pressed keys
        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.jump = False
        self.key_shoot = False
        self.key_special = False

        self.gold = gold

        # external groups
        self.enemies = enemies
        self.gold_group = gold_group
        self.bullet_group = bullet_group
        self.texts = texts

        # shooting
        if selected_gun == "handgun":
            self.gun = Handgun(self.bullet_group, self.vector)
            self.gun_images = load_images("data/img/guns/handgun", "handgun_", 1.5, 1)
        elif selected_gun == "shotgun":
            self.gun = Shotgun(self.bullet_group, self.vector)
            self.gun_images = load_images("data/img/guns/shotgun", "shotgun_", 1.5, 1)
        elif selected_gun == "minigun":
            self.gun = Minigun(self.bullet_group, self.vector)
            self.gun_images = load_images("data/img/guns/minigun", "minigun_", 1.5, 1)

        # apply bought upgrades
        for upgrade in upgrades:
            if upgrade == "BulletSpeedUp":
                self.gun.cooldown = int(self.gun.cooldown * 0.8)
            elif upgrade == "ManaRegen":
                self.mana_regen += 0.05
            elif upgrade == "ManaUp":
                self.max_mana += 25
                self.mana += 25
            elif upgrade == "SpeedUp":
                self.speed += 1
                self.jump_speed -= 1
            elif upgrade == "Strength":
                self.gun.damage = (self.gun.damage[0] + 1, self.gun.damage[1] + 2)

    def get_damage(self, damage: int):
        self.health -= damage
        if self.debuffs["burning"] > 0:
            color = ORANGE
        elif self.debuffs["poison"] > 0:
            color = GREEN
        else:
            color = RED
        self.texts.add(DamageText((randint(self.rect.left, self.rect.right), randint(self.rect.top - 8, self.rect.top + 8)), str(damage), color))
        self.invincible = True

    def update_action(self, new_action: str):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0

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
                    self.rect.centerx = ladder.rect.centerx - 4

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
        collision_rect = Rect(self.rect.x, self.rect.bottom, self.rect.width, 8)
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
                        self.vector.y += 8.5

                    break

    def check_lava_collisions(self, lava_tiles: set):
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

        # restore speed values if not in lava
        self.speed = 8
        self.jump_speed = -18

    def check_enemy_collisions(self):
        for enemy in self.enemies:
            if self.rect.colliderect(enemy.rect):
                damage = randint(enemy.damage[0], enemy.damage[1])
                self.get_damage(damage)
                if isinstance(enemy, SpiderAdvanced):
                    if randint(0, 5) < 2:
                        self.debuffs["poison"] = 5
                break

    def check_coins_collisions(self):
        for gold in self.gold_group:
            if self.rect.colliderect(gold.rect):
                self.gold += gold.amount
                self.texts.add(DamageText(self.rect.midtop, f"{gold.amount}$", GOLD))
                gold.kill()
                return gold.amount * 10
        return

    def draw(self, screen: Surface, scroll: set):
        screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

    def update(self, screen: Surface, scroll: list, objects: dict):
        # update x position and check for horizontal collisions
        self.rect.x += self.vector.x
        self.check_horizontal_collisions(objects["collidable"])
        
        # update y position and check for verical collisions
        self.vector.y += GRAVITY
        self.rect.y += self.vector.y
        self.check_vertical_collisions(objects["collidable"])

        # check for collisions with other objects (except enemies)
        self.check_ladder_collisions(objects["ladders"])
        self.check_platform_collisions(objects["platforms"])
        self.check_lava_collisions(objects["lava"])
        score = self.check_coins_collisions()

        # update shoot cooldown
        if self.gun.cooldown > 0:
            self.gun.cooldown -= 1

        # regenerate mana
        if self.mana < self.max_mana:
            self.mana += self.mana_regen

        # shoot
        if self.key_shoot:
            self.gun.shoot(self.rect, self.flip, self.up, self.down)
        # special
        if self.key_special:
            self.mana = self.gun.special(self.rect, self.flip, self.mana, self.up, self.down)

        # move left
        if self.left:
            if not self.climbing:
                self.vector.x = -self.speed
                self.update_action("run")
            self.flip = True
        # or move right
        elif self.right:
            if not self.climbing:
                self.vector.x = self.speed
                self.update_action("run")
            self.flip = False
        # or stop moving
        else:
            self.vector.x = 0
            if not self.climbing:
                self.update_action("idle")
        # jump (from ground or from ladder)
        if (self.jump and self.on_ground) or (self.jump and self.climbing):
            self.vector.y = self.jump_speed
            self.jump = False
            self.on_ground = False
            self.climbing = False

        # set max falling speed
        if self.vector.y > 18:
            self.vector.y = 18

        if not self.climbing and not self.on_ground:
            self.update_action("jump")
        elif self.climbing:
            self.update_action("climb")

        # check for collisions with enemies
        if not self.invincible:
            self.check_enemy_collisions()
            # get damage from debuffs
            if self.debuffs["burning"] > 0:
                self.get_damage(2)
                self.debuffs["burning"] -= 1
            if self.debuffs["poison"] > 0:
                self.get_damage(1)
                self.debuffs["poison"] -= 1

        # update invincivbility
        if self.invincible:
            self.invincibility_duration -= 1
            if self.invincibility_duration <= 0:
                self.invincibility_duration = 90
                self.invincible = False

        # change animation frame
        if not self.climbing or (self.climbing and self.up or self.down):
            self.frame_index += self.cooldowns[self.action]
        if self.frame_index >= len(self.animations[self.action]):
            self.frame_index = 0
        # set new frame to the image and flip it if necessary
        self.image = flip(self.animations[self.action][floor(self.frame_index)], self.flip, False)

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

        # draw gun
        if not self.climbing:
            if not self.on_ground:
                if self.up:
                    offset_y = -16
                else:
                    offset_y = -8
            else:
                offset_y = 0

            if not self.up and not self.down:
                if not self.flip:
                    screen.blit(self.gun_images[0], (self.rect.x - scroll[0], self.rect.y - scroll[1] + offset_y))
                else:
                    image = flip(self.gun_images[0], True, False)
                    image_rect = image.get_rect(topright=(self.rect.right - scroll[0], self.rect.y - scroll[1] + offset_y))
                    screen.blit(image, image_rect)
            elif self.up:
                if not self.flip:
                    screen.blit(self.gun_images[1], (self.rect.x - scroll[0], self.rect.y - scroll[1] + offset_y))
                else:
                    image = flip(self.gun_images[1], True, False)
                    image_rect = image.get_rect(topright=(self.rect.right - scroll[0], self.rect.y - scroll[1] + offset_y))
                    screen.blit(image, image_rect)
            elif self.down:
                if not self.flip:
                    screen.blit(self.gun_images[2], (self.rect.x - scroll[0], self.rect.y - scroll[1] + offset_y))
                else:
                    image = flip(self.gun_images[2], True, False)
                    image_rect = image.get_rect(topright=(self.rect.right - scroll[0], self.rect.y - scroll[1] + offset_y))
                    screen.blit(image, image_rect)

        return score


class EnemyBase(Sprite):
    def __init__(self, position: tuple, hp: int, damage: tuple, speed: tuple, gold: tuple, gold_group: Group):
        super().__init__()

        self.gold_group = gold_group

        # image and rect
        self.image = Surface((TILE_SIZE // 2, TILE_SIZE - 8))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(position[0], position[1]))

        # health, damage, speed and gold amount from config file
        if isinstance(hp, tuple):
            self.health = randint(hp[0], hp[1])
        else:
            self.health = hp

        self.damage = tuple(damage)

        if isinstance(speed, tuple):
            self.speed = randint(speed[0], speed[1])
        else:
            self.speed = speed

        if isinstance(gold, tuple):
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
            return self.score_amount

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


class Slime(EnemyBase):
    def __init__(self, position: tuple, images: tuple, gold_group: Group):
        super().__init__(position, 10, (1, 3), (1, 3), (0, 2), gold_group)
        self.animation = images
        self.frame_index = 0
        self.animation_length = len(images)
        self.image = self.animation[self.frame_index]
        self.rect = Rect(position[0], position[1], 48, 48)
        self.flip = False

        self.score_amount = 30

        self.vector.x = self.speed * choice((-1, 1))

    def draw(self, screen: Surface, scroll: list):
        screen.blit(self.image, (self.rect.x - 8 - scroll[0], self.rect.y - 16 - scroll[1]))

    def update(self, screen: Surface, scroll: list, tiles: set, platforms: set, player_rect: Rect, constraints: Group):
        if self.vector.x > 0:
            self.flip = True
        elif self.vector.x < 0:
            self.flip = False
        # update animation frame
        self.frame_index += 0.2
        if self.frame_index >= self.animation_length:
            self.frame_index = 0
        # set new frame to the image and flip it if necessary
        self.image = flip(self.animation[floor(self.frame_index)], self.flip, False)

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


class Spider(EnemyBase):
    def __init__(self, position: tuple, images: tuple, gold_group: Group):
        super().__init__(position, 6, (1, 2), (5, 6), (0, 2), gold_group)

        self.animations = {"idle": images[0], "run": images[1]}
        self.frame_index = 0
        self.action = "idle"
        self.cooldowns = {"idle": 0.2, "run": 0.4}
        self.image = self.animations[self.action][self.frame_index]

        self.score_amount = 60

        self.vector.x = self.speed * choice((-1, 1))

        self.rect = self.image.get_rect(topleft=position)

    def update_action(self, new_action: str):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0

    def check_constraints(self, constraints: set):
        for constraint in constraints:
            if self.rect.colliderect(constraint):
                self.vector.x *= -1

    def update(self, screen: Surface, scroll: list, tiles: set, platforms: set, player_rect: Rect, constraints: Group):
        if not self.idling:
            # random idle
            if randint(1, 50) == 1:
                self.idling = True
                self.update_action("idle")
                self.idling_counter = randint(30, 70)
                
            # update x position and check for horizontal collisions
            self.rect.x += self.vector.x
            self.check_horizontal_collisions(tiles)
            self.check_constraints(constraints)
        else:
            self.idling_counter -= 1
            # after idle - stop idling, randomly select direction of moving
            if self.idling_counter <= 0:
                self.idling = False
                self.update_action("run")
                self.vector.x *= choice((-1, 1))

        # update y position and check collisions with tiles
        self.vector.y += GRAVITY
        self.rect.y += self.vector.y
        self.check_vertical_collisions(set.union(tiles, platforms))

        # set max falling spedd - temp fix for bug with platform collision
        if self.vector.y > 18:
            self.vector.y = 18

        # update animation frame
        self.frame_index += self.cooldowns[self.action]
        if self.frame_index >= len(self.animations[self.action]):
            self.frame_index = 0
        # set new frame to the image and flip it if necessary
        self.image = self.animations[self.action][floor(self.frame_index)]

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


class SpiderAdvanced(EnemyBase):
    def __init__(self, position: tuple, images: tuple, gold_group: Group):
        super().__init__(position, 6, (1, 2), (5, 6), (0, 2), gold_group)

        self.animations = {"idle": images[0], "run": images[1]}
        self.frame_index = 0
        self.action = "idle"
        self.cooldowns = {"idle": 0.2, "run": 0.4}
        self.image = self.animations[self.action][self.frame_index]
        self.flip = False

        self.score_amount = 120

        self.rect = self.image.get_rect(topleft=position)
        self.vision_rect = Rect(0, 0, 640, 240)

    def update_action(self, new_action: str):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0

    def check_constraints(self, constraints: set):
        for constraint in constraints:
            if self.rect.colliderect(constraint):
                self.vector.x *= -1

    def update(self, screen: Surface, scroll: list, tiles: set, platforms: set, player_rect: Rect, contraints: Group):
        if not self.idling:
            # random idle
            if randint(1, 50) == 1:
                self.idling = True
                self.update_action("idle")
                self.idling_counter = randint(30, 70)
                
            # update x position and check for horizontal collisions
            self.rect.x += self.vector.x
            self.check_horizontal_collisions(tiles)
            self.check_constraints(contraints)
        else:
            self.idling_counter -= 1
            # after idle - stop idling, randomly select direction of moving
            if self.idling_counter <= 0:
                self.idling = False
                self.update_action("run")
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
            self.update_action("run")
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

        if self.vector.x < 0:
            self.flip = False
        elif self.vector.x > 0:
            self.flip = True
        # update animation frame
        self.frame_index += self.cooldowns[self.action]
        if self.frame_index >= len(self.animations[self.action]):
            self.frame_index = 0
        # set new frame to the image and flip it if necessary
        self.image = flip(self.animations[self.action][floor(self.frame_index)], self.flip, False)

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


class Bat(EnemyBase):
    def __init__(self, position: tuple, images: tuple, gold_group: Group):
        super().__init__(position, 10, (1, 3), (4, 6), (0, 4), gold_group)

        self.animations = {"idle": images[0], "fly": images[1]}
        self.frame_index = 0
        self.action = "idle"
        self.cooldowns = {"idle": 0.01, "fly": 0.25}
        self.image = self.animations[self.action][self.frame_index]
        self.flip = False

        self.vision_rect = Rect(0, 0, 640, 360)
        self.spotted_player = False

        self.score_amount = 120

        self.move_count = 30

    def check_horizontal_collisions(self, tiles: set):
        for tile in tiles:
            if tile.rect.colliderect(self.rect):
                # touching tile right wall
                if self.vector.x < 0:
                    self.rect.left = tile.rect.right
                    if not self.spotted_player:
                        random_angle = randint(-90, 90)
                        self.vector.x = round(self.speed * cos(radians(random_angle)))
                        self.vector.y = round(self.speed * sin(radians(random_angle)))
                    break
                # touching tile left wall
                elif self.vector.x > 0:
                    self.rect.right = tile.rect.left
                    if not self.spotted_player:
                        random_angle = randint(90, 270)
                        self.vector.x = round(self.speed * cos(radians(random_angle)))
                        self.vector.y = round(self.speed * sin(radians(random_angle)))
                        break

    def check_vertical_collisions(self, tiles: set):
        for tile in tiles:
            if tile.rect.colliderect(self.rect):
                # touching floor
                if self.vector.y > 0:
                    self.rect.bottom = tile.rect.top
                    if not self.spotted_player:
                        random_angle = randint(180, 360)
                        self.vector.x = round(self.speed * cos(radians(random_angle)))
                        self.vector.y = round(self.speed * sin(radians(random_angle)))
                        break
                # touching ceiling
                elif self.vector.y < 0:
                    self.rect.top = tile.rect.bottom
                    if not self.spotted_player:
                        random_angle = randint(0, 180)
                        self.vector.x = round(self.speed * cos(radians(random_angle)))
                        self.vector.y = round(self.speed * sin(radians(random_angle)))
                        break

    def get_damage(self, damage: int):
        self.update_action("fly")
        self.health -= damage
        self.blinking = 30
        if self.health <= 0:
            if self.gold_amount > 0:
                self.gold_group.add(Gold((randint(self.rect.left, self.rect.right), self.rect.bottom), self.gold_amount))
            self.kill()
            return self.score_amount

    def update_action(self, new_action: str):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0

    def update(self, screen: Surface, scroll: list, tiles: set, platforms: set, player_rect: Rect, constraints: Group):
        if self.action == "fly":
            if self.vector.x > 0:
                self.flip = True
            elif self.vector.x < 0:
                self.flip = False
            # update animation frame
            self.frame_index += 0.2
            if self.frame_index >= len(self.animations[self.action]):
                self.frame_index = 0
            # set new frame to the image and flip it if necessary
            self.image = flip(self.animations[self.action][floor(self.frame_index)], self.flip, False)

            if self.move_count == 0:
                random_angle = randint(1, 360)
                self.vector.x = round(self.speed * cos(radians(random_angle)))
                self.vector.y = round(self.speed * sin(radians(random_angle)))
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

        # update enemy vision
        self.vision_rect.center = self.rect.center
        # if enemy "sees" the player
        if self.vision_rect.colliderect(player_rect):
            self.update_action("fly")
            self.idling = False
            self.spotted_player = True
            self.move_count = 10
            # change enemy direction to go after the player
            x_distance = player_rect.centerx - self.rect.centerx
            y_distance = player_rect.centery - self.rect.centery - 24
            angle = atan2(y_distance, x_distance)
            self.vector.x = round(self.speed * cos(angle))
            self.vector.y = round(self.speed * sin(angle))
        else:
            self.spotted_player = False
            
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
