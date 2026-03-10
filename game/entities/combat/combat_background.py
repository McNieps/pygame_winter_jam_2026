from isec.app import Resource
from isec.environment import Entity, Sprite


class CombatBackground(Entity):
    def __init__(self) -> None:
        super().__init__((0, 0), Sprite(Resource.image["combat_background"], position_anchor="topleft"))
