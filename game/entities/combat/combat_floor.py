from isec.app import Resource
from isec.environment import Entity, Sprite


class CombatFloor(Entity):
    def __init__(self):
        super().__init__((0, 300),
                         Sprite(Resource.image["combat_floor"], position_anchor="bottomleft"))
