from json import dump as dump_to_json
from json import load as load_json
from random import randint

from numpy import loadtxt, uint8
from pygame.font import Font
from pygame.image import load as load_image
from pygame.locals import BLEND_RGBA_MULT
from pygame.rect import Rect
from pygame.sprite import Group
from pygame.surface import Surface
from pygame.time import Clock
from pygame.transform import scale2x

from .classes import HealthBar, ManaBar
from .constants import CHUNK_SIZE, SCREEN_SIZE, TILE_SIZE, WHITE
from .entities import Player
from .functions import load_images, screen_fade
from .tiles import Door, Lava, LavaTile, Tile, Torch


class Level:
    def __init__(self, screen: Surface, clock: Clock, save_data: dict):
        self.screen = screen
        self.clock = clock

        # game elements containers - objects/groups/sets
        self.player = None
        self.game_map = {}
        self.torch_particles = set()
        self.bullet_group = Group()
        self.enemies = Group()
        self.texts = Group()
        self.gold_group = Group()
        self.doors = Group()

        self.save_data = save_data
        self.score = 0
        self.current_map = "level_0"  # entrance level
        self.current_level = 0
        self.last_door_position = None

        # scrolling
        self.true_scroll = [0, 0]
        self.scroll = [0, 0]

        # pressed keys (looking around)
        self.key_up = False
        self.key_down = False

        # load doors data
        with open("data/maps/entrances_data.json", "r") as f:
            self.doors_data = load_json(f)

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
        self.player_light = load_image("data/img/lights/player_light.png").convert_alpha()
        self.torch_light = load_image("data/img/lights/torch_light.png").convert_alpha()
        self.torch_particle_light = load_image("data/img/lights/torch_particle_light.png").convert_alpha()
        self.bullet_light = load_image("data/img/lights/bullet_light.png").convert_alpha()
        self.lava_light = load_image("data/img/lights/lava_light.png").convert_alpha()

    def load_level(self, very_important_variable=None):
        # images
        stone_img = scale2x(scale2x(load_image("data/img/stone.png").convert()))
        bg_stone_img = scale2x(scale2x(load_image("data/img/background_stone.png").convert()))
        ladder_img = load_image("data/img/ladder.png").convert_alpha()
        platform_img = load_image("data/img/platform.png").convert_alpha()
        torch_imgs = load_images("data/img/torch", "torch_", 1, 1)
        spider_imgs = (load_images("data/img/spider_small/idle", "spider_i_", 2, 1), load_images("data/img/spider_small/run", "spider_r_", 2, 1))
        lava_imgs = load_images("data/img/lava", "Lava_", 1, 1)
        lava_img = load_image("data/img/lava.png").convert()
        doors = {4: load_image("data/img/doors/4.png").convert_alpha(), 6: load_image("data/img/doors/6.png").convert_alpha(),
                 7: load_image("data/img/doors/7.png").convert_alpha(), 8: load_image("data/img/doors/8.png").convert_alpha()}

        # load map
        map_data = loadtxt(f"data/maps/{self.current_map}.csv", dtype=uint8, delimiter=',')
        
        # update level_0
        if self.current_map == "level_0":
            # highscores door
            if self.save_data["deaths"] > 0:
                map_data[16][16] = 6
                map_data[16][15] = 5
                map_data[16][17] = 5
            # achievements door
            if self.save_data["depth"] > 0:
                map_data[9][9] = 6
                map_data[9][8] = 5
                map_data[9][10] = 5
                for i in range(11, 17):
                    map_data[i][19] = 2
            # path to achievements
            if self.save_data["depth"] > 5:
                map_data[10][13] = 5
                map_data[10][16] = 5
            if self.save_data["kills"] >= 100:
                map_data[13][27] = 5
                map_data[14][24] = 5
                map_data[15][21] = 5

        # create empty chunks structure
        # length and width of map must be a multiple of 8
        for y in range(len(map_data) // CHUNK_SIZE):
            for x in range(len(map_data[0]) // CHUNK_SIZE):
                self.game_map[f"{x};{y}"] = {"tiles": set(), "ladders": set(), "platforms": set(),
                                             "torches": set(), "lava": set(), "animated_tiles": set(),
                                             "bg_tiles": set(), "decorations": set(), "collidable": set()}

        # load level data from tuple
        for y, row in enumerate(map_data):
            current_chunk_y = y // CHUNK_SIZE
            for x, cell in enumerate(row):
                current_chunk_x = x // CHUNK_SIZE
                current_chunk = f"{current_chunk_x};{current_chunk_y}"  # calculate coordinates of chunk

                # create stone tiles and add them to chunks
                if cell == 1:
                    if y > 0 and x > 0 and y < len(map_data) - 1 and x < len(map_data[0]) - 1:
                        collidable = False
                        for i in range(-1, 2):
                            for j in range(-1, 2):
                                if i == 0 and j == 0:
                                    pass
                                else:
                                    if map_data[y + i][x + j] != 1:
                                        collidable = True
                                        break
                        if collidable:
                            self.game_map[current_chunk]["collidable"].add(Tile((x * TILE_SIZE, y * TILE_SIZE), stone_img))
                        else:
                            self.game_map[current_chunk]["tiles"].add(Tile((x * TILE_SIZE, y * TILE_SIZE), stone_img))
                # create ladders
                elif cell == 2:
                    self.game_map[current_chunk]["ladders"].add(Tile((x * TILE_SIZE, y * TILE_SIZE), ladder_img))
                # create platforms
                elif cell == 3:
                    self.game_map[current_chunk]["platforms"].add(Tile((x * TILE_SIZE, y * TILE_SIZE), platform_img))
                # create doors
                elif cell in (4, 6):
                    image_rect = doors[cell].get_rect(midbottom=(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE))
                    if self.doors_data[self.current_map][f"{x};{y}"] == "player":
                        self.doors.add(Door((image_rect.x, image_rect.y), doors[cell], None, False))
                        self.player = Player((x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE), self.enemies, self.gold_group, self.bullet_group, self.texts)
                    else:
                        self.doors.add(Door((image_rect.x, image_rect.y), doors[cell], self.doors_data[self.current_map][f"{x};{y}"], True))
                elif cell in (7, 8):
                    image_rect = doors[cell].get_rect(midbottom=(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE))
                    self.doors.add(Door((image_rect.x, image_rect.y), doors[cell], self.doors_data[self.current_map][f"{x};{y}"], False))
                # create torches
                elif cell == 5:
                    self.game_map[current_chunk]["torches"].add(Torch((x * TILE_SIZE, y * TILE_SIZE - 32), torch_imgs))
                # create lava
                elif cell == 9:
                    self.game_map[current_chunk]["lava"].add(Lava((x * TILE_SIZE, y * TILE_SIZE), lava_imgs))
                elif cell == 10:
                    self.game_map[current_chunk]["lava"].add(LavaTile((x * TILE_SIZE, y * TILE_SIZE), lava_img))
                # create background tiles
                if cell != 1:
                    self.game_map[current_chunk]["bg_tiles"].add(Tile((x * TILE_SIZE, y * TILE_SIZE), bg_stone_img))

        # positions in main rooms
        if len(self.doors) == 1:  # achievements/highscores
            door_pos = self.doors.sprites()[0].rect
            self.player = Player(door_pos.midbottom, self.enemies, self.gold_group, self.bullet_group, self.texts)
        elif very_important_variable is not None:
            self.player = Player((very_important_variable[0] * TILE_SIZE + TILE_SIZE // 2, very_important_variable[1] * TILE_SIZE + TILE_SIZE), self.enemies, self.gold_group, self.bullet_group, self.texts)
        # elif very_important_variable is None and self.current_map == "level_0":
            
        
        # center scroll to the player
        self.true_scroll[0] += (self.player.rect.x - self.true_scroll[0] - 618)
        self.true_scroll[1] += (self.player.rect.y - self.true_scroll[1] - 328)
        self.scroll[0] = int(self.true_scroll[0])
        self.scroll[1] = int(self.true_scroll[1])

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

        # max scrolls
        # if self.scroll[0] < 100:
        #     self.scroll[0] = 100
        # elif self.scroll[0] > 1190:
        #     self.scroll[0] = 1190
        # if self.scroll[1] < 100:
        #     self.scroll[1] = 100
        # elif self.scroll[1] > 704:
        #     self.scroll[1] = 704

    def restart_level(self):
        # reset all containers
        self.player = None
        self.game_map.clear()
        self.torch_particles.clear()
        self.bullet_group.empty()
        self.enemies.empty()
        self.texts.empty()
        self.gold_group.empty()
        self.doors.empty()
        # reset scroll values
        self.true_scroll[0] = 0
        self.true_scroll[1] = 0
        self.scroll[0] = 0
        self.scroll[1] = 0
        self.screen_shake = 0
        # restart keys
        self.key_up = False
        self.key_down = False

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
                   "bg_tiles": set(), "decorations": set(), "collidable": set()}

        # iterate through every active chunk
        for y in range(4):
            target_y = y - 1 + round(self.scroll[1] / (CHUNK_SIZE * TILE_SIZE))
            for x in range(5):
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
                    objects["collidable"] |= self.game_map[target_chunk]["collidable"]

        # draw background tiles
        for tile in objects["bg_tiles"]:
            tile.draw(self.screen, self.scroll)

        # draw tiles
        for tile in set.union(objects["tiles"], objects["collidable"]):
            tile.draw(self.screen, self.scroll)

        # draw doors
        for door in self.doors:
            door.draw(self.screen, self.scroll)

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
                bullet.update(self.screen, self.scroll, objects["collidable"], self.enemies, self.texts)
            else:
                bullet.kill()

        # draw gold
        for gold in self.gold_group:
            if active_rect.colliderect(gold.rect):
                gold.update(self.screen, self.scroll, set.union(objects["collidable"], objects["platforms"]))

        # update and draw enemies
        for enemy in self.enemies:
            if active_rect.colliderect(enemy.rect):
                enemy.update(self.screen, self.scroll, objects["collidable"], objects["platforms"], self.player.rect)

        # update and draw player
        self.player.update(self.screen, self.scroll, objects)

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
            darkness.fill((0, 0, 0))
            # player light
            darkness.blit(self.player_light, self.player_light.get_rect(center=(self.player.rect.centerx - self.scroll[0], self.player.rect.centery - self.scroll[1])))
            # torch lights
            for torch in objects["torches"]:
                darkness.blit(self.torch_light, self.torch_light.get_rect(center=(torch.rect.centerx - self.scroll[0], torch.rect.centery - self.scroll[1])))
            # torch particle lights
            for particle in self.torch_particles:
                darkness.blit(self.torch_particle_light, self.torch_particle_light.get_rect(center=(particle.position[0] - self.scroll[0], particle.position[1] - self.scroll[1])))
            # lava light
            for lava in objects["lava"]:
                darkness.blit(self.lava_light, self.lava_light.get_rect(center=(lava.rect.centerx - self.scroll[0], lava.rect.centery - self.scroll[1])))
            # bullet lights
            for bullet in self.bullet_group:
                darkness.blit(self.bullet_light, self.bullet_light.get_rect(center=(bullet.rect.centerx - self.scroll[0], bullet.rect.centery - self.scroll[1])))

            self.screen.blit(darkness, (0, 0), special_flags=BLEND_RGBA_MULT)

        # draw UI
        self.health_bar.draw(self.screen, self.player.health, self.player.max_health)
        self.mana_bar.draw(self.screen, self.player.mana, self.player.max_mana)
        gold_amount = self.font.render(f"$: {self.player.gold}", False, WHITE)
        self.screen.blit(gold_amount, (SCREEN_SIZE[0] - 181, 78))

        # check level changes
        for door in self.doors:
            if self.player.rect.colliderect(door.rect):
                if self.key_up and self.player.on_ground and door.allowed:
                    coords = None
                    if self.current_map in ("highscores", "achievements"):
                        for coords, name in self.doors_data["level_0"].items():
                            if name == self.current_map:
                                coords = coords.split(';')
                                coords = tuple(map(int, coords))
                                break
                    elif "level" in door.leads_to:
                        level_number = int(door.leads_to[6:])
                        if level_number > 0:
                            self.current_level += 1
                            if self.current_level - 1 > self.save_data["depth"]:
                                self.save_data["depth"] = self.current_level - 1
                            with open("save.json", "w") as f:
                                dump_to_json(self.save_data, f, indent=4)
                    self.current_map = door.leads_to
                    screen_fade(self.screen, self.clock, True)
                    self.restart_level()
                    self.load_level(coords)
                    self.run()
                    screen_fade(self.screen, self.clock, False)
