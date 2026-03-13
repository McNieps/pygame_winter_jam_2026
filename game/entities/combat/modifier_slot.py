import random
import pygame

from isec.app import Resource
from isec.environment.base import Camera
from isec.environment import Sprite, Entity

from game.battle_engine.models import Modifier
from isec.utils.oscillator import Oscillator


class ModifierSlot(Entity):
    ROTATION_AMPLITUDE = 15
    def __init__(self,
                 unit_slot: int,
                 modifier_slot: int,
                 modifier: Modifier) -> None:

        if not 0 <= unit_slot < 3:
            raise ValueError("Unit slot must be between 0-2")

        if not 0 <= modifier_slot < 3:
            raise ValueError("Modifier slot must be between 0-2")

        surface = Resource.image["modifier_slot"].copy()
        if modifier.icon:
            surface.blit(Resource.image[modifier.icon], (0, 0))

        super().__init__((45+unit_slot*55, 75+modifier_slot*20),
                         Sprite(surface, "rotated"))

        self.oscillator = Oscillator(spring_rigidity=2000, damping=0.0001)
        # self.position.a += (random.random()*2-1)*self.ROTATION_AMPLITUDE

    def update(self,
               delta: float) -> None:
        self.oscillator.update(delta)

    def display_activation(self) -> None:
        self.oscillator.impulse((random.randint(0, 1)*2-1)*750)

    def render(self,
               camera: Camera,
               surface: pygame.Surface,
               rect: pygame.Rect) -> None:

        save_a = self.position.a
        self.position.a += self.oscillator.value
        super().render(camera, surface, rect)
        self.position.a = save_a
