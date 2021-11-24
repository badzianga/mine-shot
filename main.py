# Imports ------------------------------------------------------------------- #
from sys import exit

from PIL.Image import frombytes
from PIL.ImageFilter import GaussianBlur
from pygame import init, quit
from pygame.display import set_caption, set_mode
from pygame.display import update as update_display
from pygame.event import get as get_events
from pygame.font import Font
from pygame.image import fromstring, tostring
from pygame.locals import (K_DOWN, K_ESCAPE, K_F10, K_F11, K_F12, K_LEFT,
                           K_RIGHT, K_SPACE, K_UP, KEYDOWN, KEYUP, QUIT, K_c,
                           K_x, K_z)
from pygame.time import Clock

from data.modules.constants import BLACK, FPS, RED, SCREEN_SIZE, WHITE
from data.modules.level import Level
from data.modules.menus import Menu, PauseMenu

# Init ---------------------------------------------------------------------- #
init()

screen = set_mode(SCREEN_SIZE)
set_caption("The Mine")

clock = Clock()

fps_font = Font("data/fonts/Pixellari.ttf", 40)


# Credits ------------------------------------------------------------------- #
def credits():
    # texts and their positions
    texts = ("Created by: Badzianga", "Graphics design: Piotr Szybiak")
    positions = (
        (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 4),
        (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 4 + 64),
        (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 4 + 128)
    )

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
                return
        update_display()
        clock.tick(FPS)


# Pause menu loop ----------------------------------------------------------- #
def pause_menu():
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
                    # return to main menu
                    elif menu.highlighted == 1:
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
def game_loop():
    level = Level(screen, clock)

    fps = FPS
    toggle_fps = False

    looping = True
    while looping:
        # clear screen
        screen.fill(BLACK)

        # run level
        if level.player.health > 0:
            level.run()
        # if died, return to main menu
        else:
            return

        # check events
        for event in get_events():
            if event.type == QUIT:
                quit()
                exit()

            if event.type == KEYDOWN:
                # pause game
                if event.key == K_ESCAPE:
                    looping = pause_menu()
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
                if event.key == K_x:
                    level.player.shoot()
                if event.key == K_c:
                    level.player.burst()
                # show/hide fps
                if event.key == K_F12:
                    toggle_fps = not toggle_fps
                # lock/unlock max fps
                if event.key == K_F11:
                    if fps == FPS:
                        fps = 1
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

    while True:
        # clear screen
        screen.fill(BLACK)

        # draw menu (texts)
        menu.draw(screen)

        # check events
        for event in get_events():
            if event.type == QUIT:
                quit()
                exit()

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    quit()
                    exit()
                # select highlighted option in menu
                if event.key in (K_SPACE, K_z):
                    # start new game
                    if menu.highlighted == 0:
                        game_loop()
                    # load game
                    elif menu.highlighted == 1:
                        pass
                    # options
                    elif menu.highlighted == 2:
                        pass
                    # credits
                    elif menu.highlighted == 3:
                        credits()
                    # quit game
                    elif menu.highlighted == 4:
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


main_menu()
