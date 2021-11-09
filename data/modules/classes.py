import pygame

from .constants import BROWN, LIGHT_PURPLE, MAP, SCREEN_SIZE, TILE_SIZE, WHITE
from .entities import Enemy, Player
from .functions import load_images
from .tiles import AnimatedTile, Lava, Tile, Torch


class HealthBar:
    def __init__(self):
        self.health_border = pygame.transform.scale2x(pygame.image.load("data/img/health_border.png").convert_alpha())
        self.health_bar = pygame.transform.scale2x(pygame.image.load("data/img/health_bar.png").convert_alpha())
        self.size = self.health_bar.get_size()

    def update(self, screen, health, max_health):
        # draw border
        screen.blit(self.health_border, (SCREEN_SIZE[0] - 185, 18))  # border
        # draw current health
        screen.blit(
            self.health_bar,
            (SCREEN_SIZE[0] - 181, 20),
            (0, 0, int(self.size[0] * (health / max_health)), self.size[1])  # width of the bar
        )


class Level:
    def __init__(self, screen):
        self.screen = screen

        # groups and single objects
        self.tiles = pygame.sprite.Group()
        self.lava = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.ladders = pygame.sprite.Group()
        self.torches = pygame.sprite.Group()
        self.torch_particles = set()
        self.enemies = pygame.sprite.Group()
        self.animated_tiles = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.player = None

        # scrolling
        self.true_scroll = [0, 0]
        self.scroll = [0, 0]

        # pressed keys
        self.key_up = False
        self.key_down = False

        # load level - load tiles to self.tiles
        self.load_level()

        # user interface
        self.health_bar = HealthBar()

    def load_level(self):
        # images 
        stone_img = pygame.transform.scale2x(pygame.transform.scale2x(pygame.image.load("data/img/stone.png").convert()))
        ladder_img = pygame.image.load("data/img/ladder.png").convert_alpha()
        torch_imgs = load_images("data/img/torch", "torch_", 1, 1)
        platform_img = pygame.Surface((TILE_SIZE, int(TILE_SIZE * 1/8)))
        platform_img.fill(BROWN)
        spider_imgs = load_images("data/img/spider", "Spider_", 1, 1)
        lava_imgs = load_images("data/img/lava", "Lava_", 1, 1)

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
                # create enemies
                elif cell == "E":
                    self.enemies.add(Enemy((x * TILE_SIZE, y * TILE_SIZE)))
                elif cell == "_":
                    self.platforms.add(Tile((x * TILE_SIZE, y * TILE_SIZE), platform_img))
                elif cell == "~":
                    self.lava.add(Lava((x * TILE_SIZE, y * TILE_SIZE), lava_imgs))
                elif cell == "S":
                    self.animated_tiles.add(AnimatedTile((x * TILE_SIZE, y * TILE_SIZE), spider_imgs, 0.1))

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

        # update and draw platforms
        self.platforms.update(self.screen, self.scroll)

        # update and draw animated tiles
        self.animated_tiles.update(self.screen, self.scroll)

        # update and draw torches, create particles
        self.torches.update(self.screen, self.scroll, self.torch_particles)

        # update bullets
        self.bullets.update(self.screen, self.scroll, self.tiles, self.enemies)

        # update and draw enemies
        self.enemies.update(self.screen, self.scroll, self.tiles)

        # update and draw player
        self.player.update(self.screen, self.scroll,
                           self.tiles, self.platforms, self.ladders,
                           self.enemies, self.lava, self.bullets)

        # update and draw lava
        self.lava.update(self.screen, self.scroll)

        # update and draw torch particles
        for particle in self.torch_particles.copy():
            particle.update(self.screen, self.scroll)
            if particle.timer <= 0:
                self.torch_particles.remove(particle)

        # draw UI
        self.health_bar.update(self.screen, self.player.health, self.player.max_health)


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
