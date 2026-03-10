import pygame
import math, time

from isec.instance.base_instance import BaseInstance
from isec.environment import EntityScene
from isec.transforms.fake_rotate_x import fake_rotate_x

from game.entities.combat.combat_background import CombatBackground
from game.entities.combat.back_snow_layer import BackSnowLayer
from game.entities.combat.front_snow_layer import FrontSnowLayer
from game.entities.combat.iron_bar import IronBar
from game.entities.combat.data_sign import DataSign
from game.entities.combat.combat_floor import CombatFloor

from game.scenes.combat_sign import CombatSign


class CombatInstance(BaseInstance):
    def __init__(self):
        super().__init__(120)
        self.background_scene = EntityScene(120, entities=[CombatBackground(), BackSnowLayer(), IronBar(), CombatFloor()])
        self.left_combat_sign_scene = CombatSign("left")
        self.right_combat_sign_scene = CombatSign("right")

        self.foreground_scene = EntityScene(120, entities=[FrontSnowLayer()])

    async def loop(self):
        self.background_scene.update(self.delta)
        self.foreground_scene.update(self.delta)


        self.background_scene.render()
        self.left_combat_sign_scene.render()
        self.right_combat_sign_scene.render()
        self.window.blit(self.left_combat_sign_scene.surface, (0, 25))
        self.window.blit(self.right_combat_sign_scene.surface, (200, 25))
        self.foreground_scene.render()
