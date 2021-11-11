from pygame.image import load
from pygame.sprite import Group
from pygame.surface import Surface
from pygame.transform import scale2x

from .classes import HealthBar
from .constants import CHUNK_SIZE, MAP, TILE_SIZE
from .entities import Player
from .tiles import Tile


class Level:
    def __init__(self, screen: Surface):
        self.screen = screen

        self.player = None
        self.game_map ={}

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

        # create empty chunks structure
        # length and width of map must be a multiple of 8!
        for y in range(len(MAP) // CHUNK_SIZE):
            for x in range(len(MAP[0]) // CHUNK_SIZE):
                self.game_map[f"{x};{y}"] = {"tiles": Group()}

        # load level data from tuple
        for y, row in enumerate(MAP):
            current_chunk_y = y // CHUNK_SIZE
            for x, cell in enumerate(row):
                current_chunk_x = x // CHUNK_SIZE

                current_chunk = f"{current_chunk_x};{current_chunk_y}"

                # create stone tiles and add them to chunks
                if cell == "X":
                    self.game_map[current_chunk]["tiles"].add(Tile((x * TILE_SIZE, y * TILE_SIZE), stone_img))
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

        # look up and down
        if self.key_up:
            self.true_scroll[1] -= 6.5
        if self.key_down:
            self.true_scroll[1] += 6.5

        # create set with tiles from active chunks - for collisions, especially enemy collisions
        active_tiles = set()

        # iterate through every active chunk
        for y in range(3):
            target_y = y - 1 + round(self.scroll[1] / (CHUNK_SIZE * TILE_SIZE))
            for x in range(4):
                target_x = x - 1 + round(self.scroll[0] / (CHUNK_SIZE * TILE_SIZE))
                target_chunk = f"{target_x};{target_y}"  # calculate coordinates of the active chunk
                if target_chunk in self.game_map.keys():
                    # iterate through every tile in chunk
                    for tile in self.game_map[target_chunk]["tiles"]:
                        tile.draw(self.screen, self.scroll)  # draw tile
                        active_tiles.add(tile)  # add tile to active_tiles for later collision checks

        # update and draw player
        self.player.update(self.screen, self.scroll, active_tiles)

        # draw UI
        self.health_bar.draw(self.screen, self.player.health, self.player.max_health)
