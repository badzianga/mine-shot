# Imports ------------------------------------------------------------------- #
from sys import exit

import pygame
from pygame.locals import (K_DOWN, K_ESCAPE, K_LEFT, K_RIGHT, K_SPACE, K_UP,
                           KEYDOWN, KEYUP, QUIT, K_z)

from data.modules.classes import Level, Menu
from data.modules.constants import BLACK, FPS, SCREEN_SIZE

# Init ---------------------------------------------------------------------- #
pygame.init()

screen = pygame.display.set_mode(SCREEN_SIZE , 0, 32)
pygame.display.set_caption("The Mine")

clock = pygame.time.Clock()

level = Level(screen)


# Game loop ----------------------------------------------------------------- #
def game_loop():
    while True:
        # clear screen
        screen.fill(BLACK)

        # run level
        level.run()

        # check events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    exit()
                # move player left
                if event.key == K_LEFT:
                    level.player.left = True
                # move player left
                if event.key == K_RIGHT:
                    level.player.right = True
                # jump
                if event.key in (K_SPACE, K_z):
                    level.player.jump = True
                # look up
                if event.key == K_UP:
                    level.key_up = True
                # look down
                if event.key == K_DOWN:
                    level.key_down = True

            if event.type == KEYUP:
                # stop moving player left
                if event.key == K_LEFT:
                    level.player.left = False
                # stop moving player right
                if event.key == K_RIGHT:
                    level.player.right = False
                # stop looking up
                if event.key == K_UP:
                    level.key_up = False
                # stop looking down
                if event.key == K_DOWN:
                    level.key_down = False

        pygame.display.update()
        clock.tick(FPS)


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
