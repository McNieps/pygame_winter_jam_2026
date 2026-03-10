from isec.app import Resource
from isec.environment import Entity, Sprite


class IronBar(Entity):
    def __init__(self) -> None:
        super().__init__((0, 10), Sprite(Resource.image["iron_bar"], position_anchor="topleft"))
