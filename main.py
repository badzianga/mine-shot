# Imports ------------------------------------------------------------------- #
from sys import exit

import pygame
from pygame.locals import (K_DOWN, K_ESCAPE, K_F11, K_F12, K_LEFT, K_RIGHT,
                           K_SPACE, K_UP, KEYDOWN, KEYUP, QUIT, K_x, K_z)

from data.modules.classes import Menu
from data.modules.constants import BLACK, FPS, RED, SCREEN_SIZE
from data.modules.level import Level

# Init ---------------------------------------------------------------------- #
pygame.init()

screen = pygame.display.set_mode(SCREEN_SIZE , 0, 32)
pygame.display.set_caption("The Mine")

clock = pygame.time.Clock()

fps_font = pygame.font.Font("data/fonts/Pixellari.ttf", 40)

# Game loop ----------------------------------------------------------------- #
def game_loop():
    level = Level(screen)

    fps = FPS
    toggle_fps = False

    while True:
        # clear screen
        screen.fill(BLACK)

        # run level
        if level.player.health > 0:
            level.run()
        # if died, return to main menu
        else:
            return

        # check events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()

            if event.type == KEYDOWN:
                # return to main menu
                if event.key == K_ESCAPE:
                    return
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
                    level.player.shoot(level.bullets)
                # show/hide fps
                if event.key == K_F12:
                    toggle_fps = not toggle_fps
                # lock/unlock max fps
                if event.key == K_F11:
                    if fps == FPS:
                        fps = 10000
                    else:
                        fps = FPS

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
        pygame.display.update()
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
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    exit()
                # select highlighted option in menu
                if event.key in (K_SPACE, K_z):
                    # start game
                    if menu.highlighted == 0:
                        game_loop()
                    # quit game
                    elif menu.highlighted == 1:
                        pygame.quit()
                        exit()
                # move highlight up
                if event.key == K_UP:
                    menu.key_up = True
                # move highlight down
                if event.key == K_DOWN:
                    menu.key_down = True

        # update menu (change highlight)
        menu.update()
        pygame.display.update()
        clock.tick(FPS)


main_menu()
