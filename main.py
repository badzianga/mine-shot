# Imports ------------------------------------------------------------------- #
from sys import exit

import pygame
from pygame.locals import K_ESCAPE, KEYDOWN, QUIT

# Init ---------------------------------------------------------------------- #
pygame.init()

screen = pygame.display.set_mode((1280, 720), 0, 32)
pygame.display.set_caption("The Mine")

clock = pygame.time.Clock()

# Main loop ----------------------------------------------------------------- #
while True:
    screen.fill((0, 0, 0))

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
