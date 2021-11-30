from os import listdir
from pygame.surface import Surface
from pygame.time import Clock
from .constants import BLACK, FPS, SCREEN_SIZE
from pygame.display import update as update_display
from pygame.image import load
from pygame.transform import smoothscale, scale2x

def load_images(path: str, filename: str, scale=1, start_counter=0) -> tuple:
    frames = []
    for i in range(start_counter, len(listdir(path)) + start_counter):
        frame = load(f"{path}/{filename}{i}.png").convert_alpha()
        if scale == 2:
            frame = scale2x(frame)
        elif scale != 1:
            frame = smoothscale(frame, (frame.get_width() * scale, frame.get_height() * scale))
        frames.append(frame)
    return tuple(frames)


def screen_fade(screen: Surface, clock: Clock, fading: bool):
    screen_copy = screen.copy()
    fade_surface = Surface(SCREEN_SIZE)
    fade_surface.fill(BLACK)
    if fading:
        alphas = range(0, 257, 24)
    else:
        alphas = range(256, -2, -24)
    for alpha in alphas:
        fade_surface.set_alpha(alpha)
        screen.blit(screen_copy, (0, 0))
        screen.blit(fade_surface, (0, 0))
        update_display()
        clock.tick(FPS)
