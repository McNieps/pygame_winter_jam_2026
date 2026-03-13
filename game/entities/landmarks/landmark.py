import pygame

from isec.app import Resource
from isec.environment import Entity, Sprite


class Landmark(Entity):
    LANDMARK_SPRITE: Sprite = None
    DESCRIPTION = ""

    def __init__(self,
                 world_position: pygame.math.Vector2,
                 coords: tuple[int, int]):

        self.coords = coords

        if self.LANDMARK_SPRITE is None:
            self.SPRITE = Sprite(Resource.image["landmarks"][self.__class__.__name__.lower()])

        super().__init__(world_position, self.SPRITE)

        self.rect = self.SPRITE.rect.move(world_position)

class Village(Landmark):
    DESCRIPTION = "A frozen village where folk still barter for bread."

class Town(Landmark):
    DESCRIPTION = "Great walled borough, hallowed from the frost’s bite."

class Stubbing(Landmark):
    DESCRIPTION = "Felled holt where hungry beasts prowl the stumps."

class Moor(Landmark):
    DESCRIPTION = "Wide white waste;\nhere dwell the wild things."

class Hallow(Landmark):
    DESCRIPTION = "Sacred shrine to bless the steel of thy blade."

class Crossing(Landmark):
    DESCRIPTION = "Broken span where lawless men wait in shadows."

class Barrow(Landmark):
    DESCRIPTION = "Ancient mound of kings;\nold iron rests within."
