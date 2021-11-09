from os import listdir

import pygame


def load_images(path, filename, scale=1, start_counter=0):
    frames = []
    for i in range(start_counter, len(listdir(path)) + start_counter):
        frame = pygame.image.load(f"{path}/{filename}{i}.png").convert_alpha()
        if scale == 2:
            frame = pygame.transform.scale2x(frame)
        frames.append(frame)
    return tuple(frames)
