import random
import pygame

from isec.app import Resource
from isec.environment import Sprite, Entity

from game.battle_engine.models import Weapon
from game.utils.oscillator import Oscillator
from game.utils.pie_reveal import apply_pie_mask
from isec.environment.base import Camera


class WeaponSlot(Entity):
    BASE_ROTATION_AMPLITUDE = 5

    def __init__(self,
                 weapon_slot: int,
                 weapon: Weapon) -> None:

        self.weapon = weapon
        self.cooldown_remaining: int = 0
        if not 0 <= weapon_slot < 3:
            raise ValueError(f"Weapon slot must be between 0-2  {weapon_slot}")

        surface = Resource.image["item_slot"].copy()
        if self.weapon.icon:
            surface.blit(Resource.image[self.weapon.icon], (5, 5))

        super().__init__((45 + weapon_slot * 55, 35),
                         Sprite(surface, "rotated"))

        self.oscillator = Oscillator(spring_rigidity=2000, damping=0.0001)
        self.position.a += (random.random()*2-1)*self.BASE_ROTATION_AMPLITUDE

    def increment_cooldown(self) -> None:
        self.cooldown_remaining += 1

    def update(self,
               delta: float) -> None:

        self.oscillator.update(delta)
        self.update_image()

    def update_image(self):
        surface = Resource.image["item_slot"].copy()
        if self.weapon.icon:
            surface.blit(Resource.image[self.weapon.icon], (5, 5))

        cooldown_surf = Resource.image["weapon_cooldown"].copy()
        apply_pie_mask(cooldown_surf,
                       self.cooldown_remaining/self.weapon.cooldown_ticks_max,
                       0,
                       False)

        surface.blit(cooldown_surf, (0, 0))
        self.sprite.surface = surface

    def display_activation(self) -> None:
        self.oscillator.impulse((random.randint(0, 1)*2-1)*750)
        self.cooldown_remaining -= self.weapon.cooldown_ticks_max

    def render(self,
               camera: Camera,
               surface: pygame.Surface,
               rect: pygame.Rect) -> None:

        save_a = self.position.a

        self.position.a += self.oscillator.value
        super().render(camera, surface, rect)
        self.position.a = save_a
