import pygame

from isec.app import Resource
from isec.environment import Entity, Sprite

from game.entities.landmarks.landmark import Landmark


class LandmarkInfo(Entity):
    TITLE_FONT: pygame.font.Font | None = None

    def __init__(self,
                 landmark: Landmark | None):

        if LandmarkInfo.TITLE_FONT is None:
            LandmarkInfo.TITLE_FONT = pygame.font.Font("game/assets/fonts/OwreKynge.ttf", 16)

        self._landmark_focused = landmark

        if landmark is None:
            super().__init__(pygame.Vector2(), Sprite(pygame.Surface((0, 0)), position_anchor="bottom"))

        else:
            super().__init__(landmark.position, Sprite(self._create_surface_for_landmark(landmark),
                                                       position_anchor="bottom"))

    def focus(self,
              landmark: Landmark) -> None:

        self._landmark_focused = landmark
        self.sprite = Sprite(self._create_surface_for_landmark(landmark), position_anchor="bottom")
        self.position = landmark.position

    def unfocus(self) -> None:
        self._landmark_focused = None
        self.sprite.displayed = False

    @classmethod
    def _create_surface_for_landmark(cls,
                                     landmark: Landmark) -> pygame.Surface:

        surface = Resource.image["landmark_info_frame"].copy()
        landmark_name = LandmarkInfo.TITLE_FONT.render(landmark.__class__.__name__.title(),
                                                       False,
                                                       Resource.data["colors"][3])
        landmark_name_rect = landmark_name.get_rect()
        landmark_name_rect.center = 76, 12
        surface.blit(landmark_name, landmark_name_rect)
        return surface
