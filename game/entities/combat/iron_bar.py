import math
import random
import warnings

from isec.app import Resource
from isec.environment import Entity, Sprite


class IronBar(Entity):
    SNOW_COMPLETE_WIDTH = 400

    def __init__(self) -> None:
        super().__init__((0, 10), Sprite(Resource.image["iron_bar"].copy(), position_anchor="topleft"))
        self.current_snow_pixel: int = 0

    def set_snow_progression(self,
                             percentage: float) -> None:

        goal_snow_pixel = min(math.ceil(self.SNOW_COMPLETE_WIDTH*percentage), self.SNOW_COMPLETE_WIDTH)
        if goal_snow_pixel < self.current_snow_pixel:
            warnings.warn("Impossible to revert snow progression")
            return

        if goal_snow_pixel == self.current_snow_pixel:
            return

        for px in range(self.current_snow_pixel, goal_snow_pixel):
            self.sprite.surface.blit(Resource.image[f"snow_accumulation_{random.randint(1,3)}"], (px, 1))

        self.current_snow_pixel = goal_snow_pixel
