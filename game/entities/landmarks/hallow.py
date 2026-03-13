import pygame.math

from isec.app import Resource
from isec.environment import Sprite

from game.entities.landmarks.landmark import Landmark


class Hallow(Landmark):
    def __init__(self, position: pygame.math.Vector2) -> None:
        super().__init__(position,
                         sprite=Sprite(Resource.image["landmarks"]["hallow"]))
