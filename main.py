# Imports ------------------------------------------------------------------- #
from sys import exit

import pygame
from pygame.locals import K_ESCAPE, KEYDOWN, QUIT

from data.modules.classes import Level
from data.modules.constants import BLACK, SCREEN_SIZE

# Init ---------------------------------------------------------------------- #
pygame.init()

screen = pygame.display.set_mode(SCREEN_SIZE , 0, 32)
pygame.display.set_caption("The Mine")

clock = pygame.time.Clock()

level = Level(screen)

# Main loop ----------------------------------------------------------------- #
while True:
    screen.fill(BLACK)

    level.run()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                exit()

    pygame.display.update()
    clock.tick(60)
