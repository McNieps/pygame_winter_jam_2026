import pygame.math

from isec.app import Resource

from isec.environment import Entity, Sprite


class BackSnowLayer(Entity):
    SCROLL_SPEED_X = 50
    SCROLL_SPEED_Y = 80

    def __init__(self) -> None:
        self.dx, self.dy = 0, 0
        super().__init__((0, 0), Sprite(Resource.image["snow_back"], position_anchor="topleft"))

    def update(self,
               delta: float) -> None:

        self.dx, self.dy = self.dx + self.SCROLL_SPEED_X*delta, self.dy + self.SCROLL_SPEED_Y*delta
        dx, self.dx = int(self.dx // 1), self.dx % 1
        dy, self.dy = int(self.dy // 1), self.dy % 1
        self.sprite.surface.scroll(dx, dy, 1)

    def scroll(self, dx, dy) -> None:
        self.dx += dx
        self.dy += dy
