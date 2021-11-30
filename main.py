# Imports ------------------------------------------------------------------- #
from json import dump as dump_to_json
from json import load as load_json
from sys import exit
from os import listdir

from PIL.Image import frombytes
from PIL.ImageFilter import GaussianBlur
from pygame import init, quit
from pygame.display import set_caption, set_mode, toggle_fullscreen, set_icon
from pygame.display import update as update_display
from pygame.event import get as get_events
from pygame.font import Font
from pygame.image import fromstring, tostring
from pygame.image import load as load_image
from pygame.locals import (K_DOWN, K_ESCAPE, K_F10, K_F11, K_F12, K_LEFT,
                           K_RIGHT, K_SPACE, K_UP, KEYDOWN, KEYUP, QUIT, K_c,
                           K_x, K_z)
from pygame.mouse import set_visible
from pygame.time import Clock

from data.modules.constants import BLACK, FPS, RED, SCREEN_SIZE, WHITE
from data.modules.level import Level
from data.modules.menus import Menu, PauseMenu, SettingsMenu
from data.modules.functions import screen_fade

# Init ---------------------------------------------------------------------- #
init()

with open("settings.json", "r") as f:
    settings = load_json(f)

screen = set_mode(SCREEN_SIZE)
set_caption("The Mine")

icon = load_image("data/img/icon.png").convert()
background_img = load_image("data/img/menu_background.png").convert()
    
set_icon(icon)

if settings["fullscreen"]:
    toggle_fullscreen()
set_visible(False)

clock = Clock()

fps_font = Font("data/fonts/Pixellari.ttf", 40)


# Credits ------------------------------------------------------------------- #
def credits():
    # texts and their positions
    texts = ("Created by: Badzianga", "Graphics design: Piotr Szybiak", "Font: Zacchary Dempsey-Plante")
    positions = (
        (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 4),
        (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 4 + 64),
        (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 4 + 128)
    )

    screen.fill(BLACK)
    for text, pos in zip(texts, positions):
        text_surf = fps_font.render(text, True, WHITE)
        text_rect = text_surf.get_rect(center=pos)
        screen.blit(text_surf, text_rect)
    screen_fade(screen, clock, False)

    while True:
        # clear screen
        screen.fill(BLACK)

        for text, pos in zip(texts, positions):
            text_surf = fps_font.render(text, True, WHITE)
            text_rect = text_surf.get_rect(center=pos)
            screen.blit(text_surf, text_rect)

        for event in get_events():
            if event.type == QUIT:
                quit()
                exit()
            if event.type == KEYDOWN:
                screen_fade(screen, clock, True)
                return
        update_display()
        clock.tick(FPS)


# Settings menu ------------------------------------------------------------- #
def settings_menu_loop():
    menu = SettingsMenu(settings)

    screen.fill(BLACK)
    menu.draw(screen)
    screen_fade(screen, clock, False)

    while True:
        # clear screen
        screen.fill(BLACK)

        # draw menu
        menu.draw(screen)

        # check events
        for event in get_events():
            if event.type == QUIT:
                # save settings before quitting
                with open("settings.json", "w") as f:
                    dump_to_json(settings, f, indent=4)
                quit()
                exit()

            if event.type == KEYDOWN:
                # leave settings menu
                if event.key == K_ESCAPE:
                    with open("settings.json", "w") as f:
                        dump_to_json(settings, f, indent=4)
                    screen_fade(screen, clock, True)
                    return
                # select highlighted option in menu
                if event.key in (K_SPACE, K_z):
                    # toggle fullscreen
                    if menu.highlighted == 0:
                        settings["fullscreen"] = not settings["fullscreen"]
                        toggle_fullscreen()
                    elif menu.highlighted == 3:
                        save_data = {"kills": 0, "deaths": 0, "depth": 0, "highscores": []}
                        with open("save.json", "w") as f:
                            dump_to_json(save_data, f, indent=4)
                            return True
                    # leave settings menu
                    elif menu.highlighted == 4:
                        with open("settings.json", "w") as f:
                            dump_to_json(settings, f, indent=4)
                        screen_fade(screen, clock, True)
                        return
                if event.key == K_LEFT:
                    # toggle fullscreen
                    if menu.highlighted == 0:
                        settings["fullscreen"] = not settings["fullscreen"]
                        toggle_fullscreen()
                    # music volume down
                    elif menu.highlighted == 1:
                        if settings["music"] > 0:
                            settings["music"] -= 10
                    # sounds volume down
                    elif menu.highlighted == 2:
                        if settings["sfx"] > 0:
                            settings["sfx"] -= 10
                if event.key == K_RIGHT:
                    # toggle fullscreen
                    if menu.highlighted == 0:
                        settings["fullscreen"] = not settings["fullscreen"]
                        toggle_fullscreen()
                    # music volume up
                    elif menu.highlighted == 1:
                        if settings["music"] < 100:
                            settings["music"] += 10
                    # sounds volume up
                    elif menu.highlighted == 2:
                        if settings["sfx"] < 100:
                            settings["sfx"] += 10
                # move highlight up
                if event.key == K_UP:
                    menu.key_up = True
                # move highlight down
                if event.key == K_DOWN:
                    menu.key_down = True

        # update menu (change highlight)
        menu.update()

        update_display()
        clock.tick(FPS)


# Pause menu loop ----------------------------------------------------------- #
def pause_menu_loop():
    # convert pygame surface to pillow image and blur it
    str_surf = tostring(screen.copy(), "RGB", False)
    blurred = frombytes("RGB", SCREEN_SIZE, str_surf).filter(GaussianBlur(5))
    # convert pillow image to pygame surface
    str_surf = blurred.tobytes("raw", "RGB")
    blurred = fromstring(str_surf, SCREEN_SIZE, "RGB")

    menu = PauseMenu()

    while True:
        screen.blit(blurred, (0, 0))
        # draw pause menu (smaller rect, without clearing screen)
        menu.draw(screen)

        # check events
        for event in get_events():
            if event.type == QUIT:
                quit()
                exit()

            if event.type == KEYDOWN:
                # unpause game
                if event.key == K_ESCAPE:
                    return True
                # select highlighted option in menu
                if event.key in (K_SPACE, K_z):
                    # unpause game
                    if menu.highlighted == 0:
                        return True
                    elif menu.highlighted == 1:
                        screen_fade(screen, clock, True)
                        reset = settings_menu_loop()
                        if reset:
                            return False
                        screen.blit(blurred, (0, 0))
                        menu.draw(screen)
                        screen_fade(screen, clock, False)
                    # return to main menu
                    elif menu.highlighted == 2:
                        screen_fade(screen, clock, True)
                        return False
                # move highlight up
                if event.key == K_UP:
                    menu.key_up = True
                # move highlight down
                if event.key == K_DOWN:
                    menu.key_down = True

        # update menu (change highlight)
        menu.update()

        update_display()
        clock.tick(FPS)


# Game loop ----------------------------------------------------------------- #
def game_loop(save_data):
    level = Level(screen, clock, save_data)

    fps = FPS
    toggle_fps = False

    screen.fill(BLACK)
    level.run()
    screen_fade(screen, clock, False)

    looping = True
    while looping:
        # clear screen
        screen.fill(BLACK)

        # run level
        if level.player.health > 0:
            level.run()
        # if died, return to main menu
        else:
            level.save_data["deaths"] += 1
            level.score += level.current_level * 100
            if len(level.save_data["highscores"]) < 5:
                level.save_data["highscores"].append(level.score)
            else:
                if level.score > min(level.save_data["highscores"]):
                    level.save_data["highscores"].remove(min(level.save_data["highscores"]))
                    level.save_data["highscores"].append(level.score)
            
            with open("save.json", "w") as f:
                    dump_to_json(level.save_data, f, indent=4)
            return

        # check events
        for event in get_events():
            if event.type == QUIT:
                with open("save.json", "w") as f:
                    dump_to_json(level.save_data, f, indent=4)
                quit()
                exit()

            if event.type == KEYDOWN:
                # pause game
                if event.key == K_ESCAPE:
                    with open("save.json", "w") as f:
                        dump_to_json(level.save_data, f, indent=4)
                    looping = pause_menu_loop()
                    # reset keys
                    level.player.left = False
                    level.player.right = False
                    level.player.up = False
                    level.player.down = False
                    level.key_up = False
                    level.key_down = False
                # move player left
                if event.key == K_LEFT:
                    level.player.left = True
                # move player right
                if event.key == K_RIGHT:
                    level.player.right = True
                # jump
                if event.key in (K_SPACE, K_z):
                    level.player.jump = True
                # look up
                if event.key == K_UP:
                    level.key_up = True
                    level.player.up = True
                # look down
                if event.key == K_DOWN:
                    level.key_down = True
                    level.player.down = True
                # shoot
                if event.key == K_x:
                    level.player.key_shoot = True
                # special
                if event.key == K_c:
                    level.player.key_special = True
                # show/hide fps
                if event.key == K_F12:
                    toggle_fps = not toggle_fps
                # lock/unlock max fps
                if event.key == K_F11:
                    if fps == FPS:
                        fps = 10000
                    else:
                        fps = FPS
                # toggle darkness effect
                if event.key == K_F10:
                    level.darkness = not level.darkness

            if event.type == KEYUP:
                # stop moving player left
                if event.key == K_LEFT:
                    level.player.left = False
                # stop moving player right
                if event.key == K_RIGHT:
                    level.player.right = False
                # stop jumping (there was a bug with double jump without it)
                if event.key in (K_SPACE, K_z):
                    level.player.jump = False
                # stop looking up
                if event.key == K_UP:
                    level.key_up = False
                    level.player.up = False
                # stop looking down
                if event.key == K_DOWN:
                    level.key_down = False
                    level.player.down = False
                # stop shooting
                if event.key == K_x:
                    level.player.key_shoot = False
                # stop special
                if event.key == K_c:
                    level.player.key_special = False

        if toggle_fps:
            screen.blit(
                fps_font.render(str(int(clock.get_fps())), False, RED),
                (8, 8)
            )
        update_display()
        clock.tick(fps)


# Main menu loop ------------------------------------------------------------ #
def main_menu():
    menu = Menu()

    screen.blit(background_img, (0, 0))
    menu.draw(screen)
    screen_fade(screen, clock, False)

    while True:
        # draw background
        screen.blit(background_img, (0, 0))

        # draw menu (texts)
        menu.draw(screen)

        # check events
        for event in get_events():
            if event.type == QUIT:
                screen_fade(screen, clock, True)
                quit()
                exit()

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    screen_fade(screen, clock, True)
                    quit()
                    exit()
                # select highlighted option in menu
                if event.key in (K_SPACE, K_z):
                    # start game
                    if menu.highlighted == 0:
                        if "save.json" in listdir():
                            with open("save.json", "r") as f:
                                save_data = load_json(f)
                        else:  # create save file if not exists
                            save_data = {"kills": 0, "deaths": 0, "depth": 0, "highscores": []}
                            with open("save.json", "w") as f:
                                dump_to_json(save_data, f, indent=4)
                        screen_fade(screen, clock, True)
                        game_loop(save_data)
                        screen.blit(background_img, (0, 0))
                        menu.draw(screen)
                        screen_fade(screen, clock, False)
                    # settings
                    elif menu.highlighted == 1:
                        screen_fade(screen, clock, True)
                        settings_menu_loop()
                        screen.blit(background_img, (0, 0))
                        menu.draw(screen)
                        screen_fade(screen, clock, False)
                    # credits
                    elif menu.highlighted == 2:
                        screen_fade(screen, clock, True)
                        credits()
                        screen.blit(background_img, (0, 0))
                        menu.draw(screen)
                        screen_fade(screen, clock, False)
                    # quit game
                    elif menu.highlighted == 3:
                        screen_fade(screen, clock, True)
                        quit()
                        exit()
                # move highlight up
                if event.key == K_UP:
                    menu.key_up = True
                # move highlight down
                if event.key == K_DOWN:
                    menu.key_down = True

        # update menu (change highlight)
        menu.update()

        update_display()
        clock.tick(FPS)


if __name__ == "__main__":
    main_menu()
