from isec.app import Resource
from isec.environment import Sprite, Entity


from game.entities.landmarks import Landmark


class Player(Entity):
    def __init__(self,
                 start_landmark: Landmark) -> None:

        self.coords = start_landmark.coords
        self.money: int = 2

        self.inventory: list[str|None] = [None for i in range(16)]

        super().__init__(start_landmark.position.xy,
                         Sprite(Resource.image["player_arrow"], position_anchor="top"))

    def move(self, landmark: Landmark) -> None:
        self.position.xy = landmark.position
        self.coords = landmark.coords
