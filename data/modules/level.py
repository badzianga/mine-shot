from random import randint
from pygame.font import Font

from pygame.image import load
from pygame.rect import Rect
from pygame.sprite import Group
from pygame.surface import Surface
from pygame.transform import scale2x
from pygame.locals import BLEND_RGBA_MULT

from .classes import HealthBar, ManaBar
from .constants import BLACK, BROWN, CHUNK_SIZE, MAP, SCREEN_SIZE, TILE_SIZE, WHITE
from .entities import Enemy, Player
from .functions import load_images
from .tiles import AnimatedTile, Lava, Tile, Torch


class Level:
    def __init__(self, screen: Surface):
        self.screen = screen

        # game elements containers - objects/groups/sets
        self.player = None
        self.game_map = {}
        self.torch_particles = set()
        self.bullet_group = Group()
        self.enemies = Group()
        self.texts = Group()
        self.gold_group = Group()

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
        self.mana_bar = ManaBar()

        # font
        self.font = Font("data/fonts/Pixellari.ttf", 32)

        # earthquake
        self.screen_shake = 0

        # darkness
        self.darkness = True
        self.player_light = load("data/img/lights/player_light.png").convert_alpha()
        self.torch_light = load("data/img/lights/torch_light.png").convert_alpha()
        self.torch_particle_light = load("data/img/lights/torch_particle_light.png").convert_alpha()
        self.bullet_light = load("data/img/lights/bullet_light.png").convert_alpha()

    def load_level(self):
        # images 
        stone_img = scale2x(scale2x(load("data/img/stone.png").convert()))
        ladder_img = load("data/img/ladder.png").convert_alpha()
        platform_img = Surface((TILE_SIZE, TILE_SIZE // 8))
        platform_img.fill(BROWN)
        torch_imgs = load_images("data/img/torch", "torch_", 1, 1)
        lava_imgs = load_images("data/img/lava", "Lava_", 1, 1)
        spider_imgs = load_images("data/img/spider", "Spider_", 1, 1)
        bg_stone_img = scale2x(scale2x(load("data/img/background_stone.png").convert()))
        decoration_imgs = load_images("data/img/decorations", "Deco_", 1, 1)

        # create empty chunks structure
        # length and width of map must be a multiple of 8
        for y in range(len(MAP) // CHUNK_SIZE):
            for x in range(len(MAP[0]) // CHUNK_SIZE):
                self.game_map[f"{x};{y}"] = {"tiles": set(), "ladders": set(), "platforms": set(),
                                             "torches": set(), "lava": set(), "animated_tiles": set(),
                                             "bg_tiles": set(), "decorations": set()}

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
                elif cell.isdigit():
                    self.game_map[current_chunk]["decorations"].add(Tile((x * TILE_SIZE, y * TILE_SIZE), decoration_imgs[int(cell) - 1]))
                # create player
                elif cell == "P":
                    self.player = Player((x * TILE_SIZE, y * TILE_SIZE))
                # create enemies
                elif cell == "E":
                    self.enemies.add(Enemy((x * TILE_SIZE, y * TILE_SIZE)))
                # create stone background tiles and add them to chunks
                if cell != "X":
                    self.game_map[current_chunk]["bg_tiles"].add(Tile((x * TILE_SIZE, y * TILE_SIZE), bg_stone_img))

    def earthquake(self):
        self.screen_shake -= 1
        self.true_scroll[0] += randint(0, 10) - 5
        self.true_scroll[1] += randint(0, 10) - 5

    def update_scroll(self):
        # first, calculate true scroll values (floats, center of the player)
        self.true_scroll[0] += (self.player.rect.x - self.true_scroll[0] - 618) / 25
        self.true_scroll[1] += (self.player.rect.y - self.true_scroll[1] - 328) / 25
        # then. convert them to integers
        self.scroll[0] = int(self.true_scroll[0])
        self.scroll[1] = int(self.true_scroll[1])

    def run(self):
        # look up and down
        if self.key_up:
            self.true_scroll[1] -= 6.5
        if self.key_down:
            self.true_scroll[1] += 6.5

        # earthquake
        if self.screen_shake > 0:
            self.earthquake()  # apply earthquake
        elif randint(1, 1000) == 1:  # 0.1% chance for earthquake
            self.screen_shake = randint(120, 180)  # 2-3s of earthquake

        # update scroll values
        self.update_scroll()

        # create set with objects from active chunks (all objects except player and enemies!)
        objects = {"tiles": set(), "ladders": set(), "platforms": set(),
                   "torches": set(), "lava": set(), "animated_tiles": set(),
                   "bg_tiles": set(), "decorations": set()}

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
                    objects["bg_tiles"] |= self.game_map[target_chunk]["bg_tiles"]
                    objects["decorations"] |= self.game_map[target_chunk]["decorations"]

        # draw background tiles
        for tile in objects["bg_tiles"]:
            tile.draw(self.screen, self.scroll)

        # draw tiles
        for tile in objects["tiles"]:
            tile.draw(self.screen, self.scroll)

        # draw decorations
        for decoration in objects["decorations"]:
            decoration.draw(self.screen, self.scroll)

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

        # create rect (slightly larger than screen rect) in which enemies and bullets will be updated
        active_rect = Rect(self.scroll[0] - 128, self.scroll[1] - 128,
                           SCREEN_SIZE[0] + 256, SCREEN_SIZE[1] + 256)

        # update and draw bullets
        for bullet in self.bullet_group.copy():
            if active_rect.colliderect(bullet.rect):
                bullet.update(self.screen, self.scroll, objects["tiles"], self.enemies, self.texts)
            else:
                bullet.kill()

        # draw gold
        for gold in self.gold_group:
            if active_rect.colliderect(gold.rect):
                gold.update(self.screen, self.scroll, set.union(objects["tiles"], objects["platforms"]))

        # update and draw enemies
        for enemy in self.enemies:
            if active_rect.colliderect(enemy.rect):
                enemy.update(self.screen, self.scroll, objects["tiles"], objects["platforms"], self.gold_group)

        # update and draw player
        self.player.update(self.screen, self.scroll, objects, self.enemies, self.texts, self.gold_group)

        # update and draw lava
        for lava in objects["lava"]:
            if active_rect.colliderect(lava.rect):
                lava.update(self.screen, self.scroll)

        # update and draw torch particles
        for particle in self.torch_particles.copy():
            particle.update(self.screen, self.scroll)
            if particle.timer < 0.5:
                self.torch_particles.remove(particle)

        # draw texts
        self.texts.update(self.screen, self.scroll)

        # darkness and light effects
        if self.darkness:
            # create darkness surface
            darkness = Surface(SCREEN_SIZE)
            darkness.fill(BLACK)
            # player light
            darkness.blit(self.player_light, self.player_light.get_rect(center=(self.player.rect.centerx - self.scroll[0], self.player.rect.centery - self.scroll[1])))
            # torch lights
            for torch in objects["torches"]:
                darkness.blit(self.torch_light, self.torch_light.get_rect(center=(torch.rect.centerx - self.scroll[0], torch.rect.centery - self.scroll[1])))
            # torch particle lights
            for particle in self.torch_particles:
                darkness.blit(self.torch_particle_light, self.torch_particle_light.get_rect(center=(particle.position[0] - self.scroll[0], particle.position[1] - self.scroll[1])))
            # bullet lights
            for bullet in self.bullet_group:
                darkness.blit(self.bullet_light, self.bullet_light.get_rect(center=(bullet.rect.centerx - self.scroll[0], bullet.rect.centery - self.scroll[1])))

            self.screen.blit(darkness, (0, 0), special_flags=BLEND_RGBA_MULT)

        # draw UI
        self.health_bar.draw(self.screen, self.player.health, self.player.max_health)
        self.mana_bar.draw(self.screen, self.player.mana, self.player.max_mana)
        gold_amount = self.font.render(f"$: {self.player.gold}", False, WHITE)
        self.screen.blit(gold_amount, (SCREEN_SIZE[0] - 181, 78))
