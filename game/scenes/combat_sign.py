import pygame

from isec.environment import EntityScene
from isec.environment.base import Camera
from isec.transforms.fake_rotate_x import fake_rotate_x

from game.entities.combat.data_sign import DataSign
from game.entities.combat.weapon_slot import WeaponSlot
from game.entities.combat.modifier_slot import ModifierSlot
from game.battle_engine.models import Weapon
from isec.utils.oscillator import Oscillator


class CombatSign(EntityScene):
    def __init__(self,
                 side: str,
                 weapons: list[Weapon]) -> None:

        super().__init__(120,
                         surface=pygame.Surface((200, 200), pygame.SRCALPHA))
        self.oscillator = Oscillator(spring_rigidity=50, damping=0.2)
        self.add_entities(DataSign(side))  # NOQA
        self.weapons: dict[str, WeaponSlot] = {}
        self.modifiers: dict[str, ModifierSlot] = {}
        for weapon_index, weapon in enumerate(weapons):
            weapon_slot = WeaponSlot(weapon_index, weapon)
            self.add_entities(weapon_slot)
            self.weapons[weapon.id] = weapon_slot

            for modifier_index, modifier in enumerate(weapon.modifiers):
                modifier_slot = ModifierSlot(weapon_index, modifier_index, modifier)
                self.add_entities(modifier_slot)
                self.modifiers[modifier.id] = modifier_slot

    def update(self,
               delta: float) -> None:

        self.oscillator.update(delta)
        super().update(delta)

    def render(self,
               camera: Camera = None) -> None:

        self.surface.fill((0, 0, 0, 0))
        super().render(camera)
        fake_rotate_x(self.surface, round(self.oscillator.value))

    def shake_sign(self, damage_percentage) -> None:
        self.oscillator.impulse(damage_percentage*1000)

    def display_weapon_activation(self, weapon_id: str) -> None:
        self.weapons[weapon_id].display_activation()

    def display_modifier_activation(self, modifier_id: str) -> None:
        self.modifiers[modifier_id].display_activation()
