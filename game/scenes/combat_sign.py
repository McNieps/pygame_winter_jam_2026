import math
import time
import pygame

from isec.environment import EntityScene
from isec.environment.base import Camera
from isec.transforms.fake_rotate_x import fake_rotate_x

from game.entities.combat.data_sign import DataSign


class CombatSign(EntityScene):
    def __init__(self,
                 side: str) -> None:

        super().__init__(120,
                         surface=pygame.Surface((200, 200), pygame.SRCALPHA))

        self.add_entities(DataSign(side))  # NOQA

    def update(self,
               delta: float) -> None:

        pass

    def render(self,
               camera: Camera = None) -> None:

        self.surface.fill((0, 0, 0, 0))
        super().render(camera)
        fake_rotate_x(self.surface, 20*math.cos(2.6*time.time()))