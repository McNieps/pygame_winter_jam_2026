import pygame

from isec.app import Resource
from isec.environment import Entity, Sprite

from game.entities.landmarks.landmark import Landmark
from game.entities.ui.go_button import GoButton
from game.entities.player import Player
from game.world_gen import MapGenerator


class LandmarkInfo(Entity):
    TITLE_FONT: pygame.font.Font | None = None
    DESCRIPTION_FONT: pygame.font.Font | None = None
    BUTTON_OFFSET = (0, -25)

    def __init__(self, player: Player, map_layout: MapGenerator):
        self.player = player
        self.map_layout = map_layout

        if LandmarkInfo.TITLE_FONT is None:
            LandmarkInfo.TITLE_FONT = pygame.font.Font("game/assets/fonts/OwreKynge.ttf", 16)
            LandmarkInfo.DESCRIPTION_FONT = pygame.font.Font("game/assets/fonts/CWEBL.ttf", 14)

        self.landmark_focused = None
        self.go_button = GoButton()
        self.go_button.active = False
        super().__init__(pygame.Vector2(), Sprite(pygame.Surface((0, 0)), position_anchor="bottom"))

        self.go_button.move(self.position+self.BUTTON_OFFSET)

    def focus(self,
              landmark: Landmark) -> None:

        self.go_button.active = False
        self.landmark_focused = landmark
        self.sprite = Sprite(self._create_surface_for_landmark(landmark), position_anchor="bottom")
        self.position = landmark.position
        self.go_button.move(self.position + self.BUTTON_OFFSET)
        if landmark.coords in self.map_layout.map[self.player.coords[0]][self.player.coords[1]].connections:
            self.go_button.active = True

    def unfocus(self) -> None:
        self.landmark_focused = None
        self.sprite.displayed = False
        self.go_button.active = False

    @classmethod
    def _create_surface_for_landmark(cls,
                                     landmark: Landmark) -> pygame.Surface:

        surface = Resource.image["landmark_info_frame"].copy()
        landmark_name = LandmarkInfo.TITLE_FONT.render(
            landmark.__class__.__name__.title(),
            False,
            Resource.data["colors"][3]
        )

        landmark_desc = LandmarkInfo.DESCRIPTION_FONT.render(
            landmark.DESCRIPTION,
            False,
            Resource.data["colors"][3],
            None,
            140
        )

        landmark_name_rect = landmark_name.get_rect()
        landmark_desc_rect = landmark_desc.get_rect()
        landmark_name_rect.center = 76, 12
        landmark_desc_rect.topleft = 5, 25
        surface.blit(landmark_name, landmark_name_rect)
        surface.blit(landmark_desc, landmark_desc_rect)
        return surface
