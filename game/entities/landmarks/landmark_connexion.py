import pygame
import random

from isec.app import Resource
from isec.environment import Entity, Sprite, Position
from isec.transforms.outline import fast_outline

from game.entities.landmarks.landmark import Landmark


class LandmarkConnexion(Entity):
    PATH_MARGIN = 16

    def __init__(self,
                 landmark_1: Landmark,
                 landmark_2: Landmark) -> None:

        path_surf: pygame.Surface = Resource.image["path"]  # .copy()
        max_length = path_surf.width

        path_vec = landmark_2.position - landmark_1.position
        path_center = (landmark_1.position + landmark_2.position)/2
        path_len = max(path_vec.length() - 2 * LandmarkConnexion.PATH_MARGIN, 0)

        offset = random.randint(0, int(max_length-path_len))
        path_surf = path_surf.subsurface((offset, 0, path_len, path_surf.height))
        # fast_outline(path_surf, Resource.data["colors"][0])
        super().__init__(position=Position(path_center),
                         sprite=Sprite(path_surf, "rotated"))

        self.position.a = -path_vec.angle
