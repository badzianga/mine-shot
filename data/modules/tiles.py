from random import randint
from pygame.rect import Rect

from pygame.sprite import Sprite
from pygame.surface import Surface

from .particles import TorchParticle


class Tile(Sprite):
    def __init__(self, position: tuple, image: Surface):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect(topleft=position)

    def draw(self, screen: Surface, scroll: list):
        screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))


class Platform(Tile):
    def __init__(self, position: tuple, image: Surface):
        super().__init__(position, image)
        self.rect = Rect(position[0], position[1], 64, 8)


class Door(Tile):
    def __init__(self, position: tuple, image: Surface, leads_to: str, allowed: bool):
        super().__init__(position, image)

        self.leads_to = leads_to
        self.allowed = allowed


class Upgrade(Tile):
    def __init__(self, position: tuple, image: Surface, type: str):
        super().__init__(position, image)

        self.type = type
        self.collision_rect = Rect(position[0], position[1] - 64, 64, 192)


class AnimatedTile(Tile):
    def __init__(self, position: tuple, images: tuple, cooldown: float):
        super().__init__(position, images[0])

        self.animation = images
        self.ANIMATION_LENGTH = len(self.animation)
        self.frame_index = 0
        self.COOLDOWN = cooldown

    def update_animation(self):
        # update animation frame
        self.frame_index += self.COOLDOWN
        if self.frame_index >= self.ANIMATION_LENGTH:
            self.frame_index = 0

        # set new frame to the image
        self.image = self.animation[int(self.frame_index)]

    def update(self, screen: Surface, scroll: list):
        self.update_animation()

        self.draw(screen, scroll)


class Lava(AnimatedTile):
    def __init__(self, position: tuple, images: tuple):
        super().__init__(position, images, 0.1)

        self.damage = (2, 3)


class LavaTile(Tile):
    def __init__(self, position: tuple, image: Surface):
        super().__init__(position, image)

        self.damage = (2, 3)

    def update(self, screen: Surface, scroll: list):
        self.draw(screen, scroll)


class Torch(AnimatedTile):
    def __init__(self, position: tuple, images: tuple):
        super().__init__(position, images, 0.25)

        self.frame_index = randint(0, self.ANIMATION_LENGTH - 1)
        self.image = self.animation[self.frame_index]

    def update(self, screen: Surface, scroll: list, particles_group: set):
        self.update_animation()

        self.draw(screen, scroll)

        # randomly generate particle
        if randint(1, 25) == 1:
            particles_group.add(
                TorchParticle([self.rect.centerx, self.rect.y + 32])
            )
