from os import listdir

import pygame


def load_images(path, filename):
    frames = []
    for i in range(1, len(listdir(path)) + 1):
        frames.append(pygame.image.load(f"{path}/{filename}_{i}.png").convert_alpha())
    return frames
