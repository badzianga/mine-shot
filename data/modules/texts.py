from pygame.font import Font, init
from pygame.sprite import Sprite
from pygame.surface import Surface

init()

font = Font("data/fonts/Pixellari.ttf", 32)


class DamageText(Sprite):
    def __init__(self, position: tuple, damage: int, color: tuple):
        super().__init__()
        self.image = font.render(damage, True, color)
        self.rect = self.image.get_rect(center=position)
        self.alpha = 255

    def draw(self, screen: Surface, scroll: list):
        screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

    def update(self, screen: Surface, scroll: list):
        # move damage text up
        self.image.set_alpha(self.alpha)
        self.alpha -= 5
        self.rect.y -= 2

        # draw text
        self.draw(screen, scroll)

        # kill sprite if it's invisible
        if self.alpha <= 0:
            self.kill()
