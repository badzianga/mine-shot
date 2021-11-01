import pygame
from pygame.locals import K_LEFT, K_RIGHT, K_SPACE, K_z

from .constants import BLUE, GRAVITY, GRAY, MAP, TILE_SIZE


class Player(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()

        # image - temporarily just a single-color surface
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(BLUE)

        # collision rect
        self.rect = self.image.get_rect(topleft=position)

        # movement stuff
        self.speed = 8
        self.vector = pygame.math.Vector2(0, 0)  # direction of movement
        self.jump_speed = -18
        self.on_ground = False

    def get_inputs(self):
        keys = pygame.key.get_pressed()

        # move left
        if keys[K_LEFT]:
            self.vector.x = -self.speed
        # or move right
        elif keys[K_RIGHT]:
            self.vector.x = self.speed
        # or stop moving
        else:
            self.vector.x = 0
        # jump
        if (keys[K_SPACE] or keys[K_z]) and self.on_ground:
            self.vector.y = self.jump_speed
            self.on_ground = False

    def check_collisions(self, tiles):
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
                # touching floor - stop falling, allow jump
                if self.vector.y > 0:
                    self.vector.y = 0
                    self.rect.bottom = tile.rect.top
                    self.on_ground = True
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

    def update(self, screen, scroll, tiles):
        # apply gravity
        self.vector.y += GRAVITY

        # get inputs and update player position
        self.get_inputs()

        # check collisions and fix position
        self.check_collisions(tiles)

        # draw player
        screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))


class Tile(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()

        # image - temporarily just a single-color surface
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(GRAY)

        # collision rect
        self.rect = self.image.get_rect(topleft=position)

    def update(self, screen, scroll):
        # draw rect
        screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))


class Level:
    def __init__(self, screen):
        self.screen = screen

        # groups and single objects
        self.tiles = pygame.sprite.Group()
        self.player = None

        # scrolling
        self.true_scroll = [0, 0]
        self.scroll = [0, 0]

        # load level - load tiles to self.tiles
        self.load_level()

    def load_level(self):
        # temporary, loads level data from tuple
        for y, row in enumerate(MAP):
            for x, cell in enumerate(row):
                # create stone tiles
                if cell == "X":
                    self.tiles.add(Tile((x * TILE_SIZE, y * TILE_SIZE)))
                # create player
                elif cell == "P":
                    self.player = Player((x * TILE_SIZE, y * TILE_SIZE))

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

        # update and draw tiles
        self.tiles.update(self.screen, self.scroll)

        # update and draw player
        self.player.update(self.screen, self.scroll, self.tiles)
