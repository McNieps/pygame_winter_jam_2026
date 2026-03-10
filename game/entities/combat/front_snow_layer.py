from isec.app import Resource
from isec.environment import Entity, Sprite


class FrontSnowLayer(Entity):
    SCROLL_SPEED_X = 400
    SCROLL_SPEED_Y = 556

    def __init__(self) -> None:
        self.dx, self.dy = 0, 0
        super().__init__((5, 0), Sprite(Resource.image["snow_front"], position_anchor="topleft"))

    def update(self,
               delta: float) -> None:

        self.dx, self.dy = self.dx + self.SCROLL_SPEED_X*delta, self.dy + self.SCROLL_SPEED_Y*delta
        dx, self.dx = int(self.dx // 1), self.dx % 1
        dy, self.dy = int(self.dy // 1), self.dy % 1
        self.sprite.surface.scroll(dy, dx, 1)
