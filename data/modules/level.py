from pygame.image import load
from pygame.surface import Surface
from pygame.transform import scale2x

from .classes import HealthBar
from .constants import BROWN, CHUNK_SIZE, MAP, TILE_SIZE
from .entities import Player
from .tiles import AnimatedTile, Lava, Tile, Torch
from .functions import load_images


class Level:
    def __init__(self, screen: Surface):
        self.screen = screen

        self.player = None
        self.game_map = {}
        self.torch_particles = set()

        # scrolling
        self.true_scroll = [0, 0]
        self.scroll = [0, 0]

        # pressed keys (looking around)
        self.key_up = False
        self.key_down = False

        # load level - create game map with chunks
        self.load_level()

        # user interface
        self.health_bar = HealthBar()

    def load_level(self):
        # images 
        stone_img = scale2x(scale2x(load("data/img/stone.png").convert()))
        ladder_img = load("data/img/ladder.png").convert_alpha()
        platform_img = Surface((TILE_SIZE, TILE_SIZE // 8))
        platform_img.fill(BROWN)
        torch_imgs = load_images("data/img/torch", "torch_", 1, 1)
        lava_imgs = load_images("data/img/lava", "Lava_", 1, 1)
        spider_imgs = load_images("data/img/spider", "Spider_", 1, 1)

        # create empty chunks structure
        # length and width of map must be a multiple of 8
        for y in range(len(MAP) // CHUNK_SIZE):
            for x in range(len(MAP[0]) // CHUNK_SIZE):
                self.game_map[f"{x};{y}"] = {"tiles": set(), "ladders": set(), "platforms": set(),
                                             "torches": set(), "lava": set(), "animated_tiles": set()}

        # load level data from tuple
        for y, row in enumerate(MAP):
            current_chunk_y = y // CHUNK_SIZE
            for x, cell in enumerate(row):
                current_chunk_x = x // CHUNK_SIZE
                current_chunk = f"{current_chunk_x};{current_chunk_y}"  # calculate coordinates of chunk

                # create stone tiles and add them to chunks
                if cell == "X":
                    self.game_map[current_chunk]["tiles"].add(Tile((x * TILE_SIZE, y * TILE_SIZE), stone_img))
                # create ladders and add them to chunks
                elif cell == "L":
                    self.game_map[current_chunk]["ladders"].add(Tile((x * TILE_SIZE, y * TILE_SIZE), ladder_img))
                # create platforms and add them to chunks
                elif cell == "_":
                    self.game_map[current_chunk]["platforms"].add(Tile((x * TILE_SIZE, y * TILE_SIZE), platform_img))
                # create torches and add them to chunks
                elif cell == "T":
                    self.game_map[current_chunk]["torches"].add(Torch((x * TILE_SIZE, y * TILE_SIZE - 32), torch_imgs))
                # create lava and add it to chunks
                elif cell == "~":
                    self.game_map[current_chunk]["lava"].add(Lava((x * TILE_SIZE, y * TILE_SIZE), lava_imgs))
                # create animated tiles (spiders) and add them to chunks
                elif cell == "S":
                    self.game_map[current_chunk]["animated_tiles"].add(AnimatedTile((x * TILE_SIZE, y * TILE_SIZE), spider_imgs, 0.1))
                # create player
                elif cell == "P":
                    self.player = Player((x * TILE_SIZE, y * TILE_SIZE))
                # TODO: load enemies

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

        # create set with objects from active chunks (all objects except player and enemies!)
        objects = {"tiles": set(), "ladders": set(), "platforms": set(),
                   "torches": set(), "lava": set(), "animated_tiles": set()}

        # iterate through every active chunk
        for y in range(3):
            target_y = y - 1 + round(self.scroll[1] / (CHUNK_SIZE * TILE_SIZE))
            for x in range(4):
                target_x = x - 1 + round(self.scroll[0] / (CHUNK_SIZE * TILE_SIZE))
                target_chunk = f"{target_x};{target_y}"  # calculate coordinates of the active chunk
                if target_chunk in self.game_map.keys():
                    # add objects from few chunks to one dict with sets
                    objects["tiles"] |= self.game_map[target_chunk]["tiles"]
                    objects["ladders"] |= self.game_map[target_chunk]["ladders"]
                    objects["platforms"] |= self.game_map[target_chunk]["platforms"]
                    objects["torches"] |= self.game_map[target_chunk]["torches"]
                    objects["lava"] |= self.game_map[target_chunk]["lava"]
                    objects["animated_tiles"] |= self.game_map[target_chunk]["animated_tiles"]

        # draw tiles
        for tile in objects["tiles"]:
            tile.draw(self.screen, self.scroll)

        # draw ladders
        for ladder in objects["ladders"]:
            ladder.draw(self.screen, self.scroll)

        # draw platforms
        for platform in objects["platforms"]:
            platform.draw(self.screen, self.scroll)

        # update and draw animated tiles
        for tile in objects["animated_tiles"]:
            tile.update(self.screen, self.scroll)

        # update and draw torches, create particles
        for torch in objects["torches"]:
            torch.update(self.screen, self.scroll, self.torch_particles)

        # update and draw player
        self.player.update(self.screen, self.scroll, objects)

        # update and draw lava
        for lava in objects["lava"]:
            lava.update(self.screen, self.scroll)

        # update and draw torch particles
        for particle in self.torch_particles.copy():
            particle.update(self.screen, self.scroll)
            if particle.timer <= 0:
                self.torch_particles.remove(particle)

        # draw UI
        self.health_bar.draw(self.screen, self.player.health, self.player.max_health)
