from random import choice, randint

import pygame

from .constants import (BLUE, GRAVITY, LIGHT_PURPLE, MAP, SCREEN_SIZE,
                        TILE_SIZE, WHITE)
from .functions import load_images


class Player(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()

        # image - temporarily just a single-color surface
        self.image = pygame.Surface((TILE_SIZE // 2, TILE_SIZE - 8))
        self.image.fill(BLUE)

        # collision rect
        self.rect = self.image.get_rect(topleft=position)

        # movement stuff
        self.speed = 8
        self.vector = pygame.math.Vector2(0, 0)  # direction of movement
        self.jump_speed = -18
        self.on_ground = False
        self.climbing = False

        # pressed keys
        self.up = False
        self.down = False
        self.left = False
        self.right = False
        self.jump = False

    def check_ladder_collisions(self, ladders):
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

    def check_tile_collisions(self, tiles):
        # update x position
        self.rect.x += self.vector.x

        # check horizontal collisions (x)
        for tile in tiles:
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
        for tile in tiles:
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

    def update(self, screen, scroll, tiles, ladders):
        # apply gravity
        self.vector.y += GRAVITY

        self.check_ladder_collisions(ladders)

        # move left
        if self.left and not self.climbing:
            self.vector.x = -self.speed
        # or move right
        elif self.right and not self.climbing:
            self.vector.x = self.speed
        # or stop moving
        else:
            self.vector.x = 0
        # jump (from ground or from ladder)
        if (self.jump and self.on_ground) or (self.jump and self.climbing):
            self.vector.y = self.jump_speed
            self.jump = False
            self.on_ground = False
            self.climbing = False

        # check collisions and fix position
        self.check_tile_collisions(tiles)

        # draw player
        screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))


class Tile(pygame.sprite.Sprite):
    def __init__(self, position, image):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect(topleft=position)

    def update(self, screen, scroll):
        # draw rect
        screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))


class Torch(pygame.sprite.Sprite):
    def __init__(self, position, images):
        super().__init__()

        self.animation = images
        self.ANIMATION_LENGTH = len(self.animation)
        self.frame_index = randint(0, self.ANIMATION_LENGTH - 1)
        self.COOLDOWN = 0.2
        self.image = self.animation[self.frame_index]

        self.rect = self.animation[0].get_rect(topleft=position)

    def update(self, screen, scroll, particles_group):
        # update animation frame
        self.frame_index += self.COOLDOWN
        if self.frame_index >= self.ANIMATION_LENGTH:
            self.frame_index = 0

        # set new frame to the image
        self.image = self.animation[int(self.frame_index)]

        # draw torch
        screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

        # randomly generate particle
        if randint(1, 25) == 1:
            particles_group.add(
                TorchParticle([self.rect.centerx, self.rect.y + 32])
            )


class TorchParticle:
    def __init__(self, position):
        self.position = position

        self.velocity = [randint(0, 10) / 10 - 0.5, -3]
        self.timer = 4.5
        self.radius = int(self.timer * 2)

        self.COLOR = choice(((235, 83, 28), (240, 240, 31), (247, 215, 36)))

    def update(self, screen, scroll: list):
        # draw particle
        pygame.draw.circle(
            screen, self.COLOR,
            (int(self.position[0] - scroll[0]), int(self.position[1] - scroll[1])),
            int(self.timer)
        )

        # change size and position of the particle
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        self.timer -= 0.04
        self.velocity[1] += 0.1
        self.radius = int(self.timer * 2)


class Level:
    def __init__(self, screen):
        self.screen = screen

        # groups and single objects
        self.tiles = pygame.sprite.Group()
        self.ladders = pygame.sprite.Group()
        self.torches = pygame.sprite.Group()
        self.torch_particles = set()
        self.player = None

        # scrolling
        self.true_scroll = [0, 0]
        self.scroll = [0, 0]

        # pressed keys
        self.key_up = False
        self.key_down = False

        # load level - load tiles to self.tiles
        self.load_level()

    def load_level(self):
        # images 
        stone_img = pygame.transform.scale2x(pygame.transform.scale2x(pygame.image.load("data/img/stone.png").convert()))
        ladder_img = pygame.image.load("data/img/ladder.png").convert_alpha()
        torch_imgs = load_images("data/img/torch", "torch")
        # temporary, loads level data from tuple
        for y, row in enumerate(MAP):
            for x, cell in enumerate(row):
                # create stone tiles
                if cell == "X":
                    self.tiles.add(Tile((x * TILE_SIZE, y * TILE_SIZE), stone_img))
                # create player
                elif cell == "P":
                    self.player = Player((x * TILE_SIZE, y * TILE_SIZE))
                # create ladders
                elif cell == "L":
                    self.ladders.add(Tile((x * TILE_SIZE, y * TILE_SIZE), ladder_img))
                # create torches
                elif cell == "T":
                    self.torches.add(Torch((x * TILE_SIZE, y * TILE_SIZE - 32), torch_imgs))
                    # I wanted torches between two tiles, that's why -32

    def update_scroll(self):
        # first, calculate true scroll values (floats, center of the player)
        self.true_scroll[0] += (self.player.rect.x - self.true_scroll[0] - 618) / 25
        self.true_scroll[1] += (self.player.rect.y - self.true_scroll[1] - 328) / 25
        # then. convert them to integers
        self.scroll[0] = int(self.true_scroll[0])
        self.scroll[1] = int(self.true_scroll[1])

    def run(self):
        # update scroll values
        self.update_scroll()

        # look up and down
        if self.key_up:
            self.true_scroll[1] -= 6.5
        if self.key_down:
            self.true_scroll[1] += 6.5

        # update and draw tiles
        self.tiles.update(self.screen, self.scroll)
        self.ladders.update(self.screen, self.scroll)

        # update and draw torches, create particles
        self.torches.update(self.screen, self.scroll, self.torch_particles)

        # update and draw player
        self.player.update(self.screen, self.scroll, self.tiles, self.ladders)

        # update and draw torch particles
        for particle in self.torch_particles.copy():
            particle.update(self.screen, self.scroll)
            if particle.timer <= 0:
                self.torch_particles.remove(particle)


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
