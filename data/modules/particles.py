from random import choice, randint

from pygame.draw import circle as draw_circle
from pygame.surface import Surface


class TorchParticle:
    def __init__(self, position: tuple):
        self.position = position

        self.velocity = [randint(0, 10) / 10 - 0.5, -3]
        self.timer = 4.5
        self.radius = int(self.timer * 2)

        self.COLOR = choice(((235, 83, 28), (240, 240, 31), (247, 215, 36)))

    def update(self, screen: Surface, scroll: list):
        # draw particle
        draw_circle(
            screen, self.COLOR,
            (int(self.position[0] - scroll[0]), int(self.position[1] - scroll[1])),
            int(self.timer)
        )

        # change size and position of the particle
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        self.timer -= 0.04
        self.velocity[1] += 0.1
        self.radius = int(self.timer * 2)
