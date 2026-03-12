import pygame
import typing

from isec.app import Resource
from isec.environment import Entity, Sprite

from game.battle_engine.models import Team

class HealthBar(Entity):
    FONT: pygame.font.Font = None

    def __init__(self,
                 side: typing.Literal["left", "right"],
                 team: Team) -> None:

        if HealthBar.FONT is None:
            HealthBar.FONT = pygame.font.Font("game/assets/fonts/CWEBS.ttf", 12)

        self.side = side
        self.team = team

        surface = Resource.image["health_bar"].copy()
        if side == "right":
            surface = pygame.transform.flip(surface, True, False)

        super().__init__((32+336*(side=="right"), 252), Sprite(surface))

        self.max_health = team.max_hp
        self.current_health = team.hp
        self.text_surf = surface.subsurface((3+(side=="right")*12, 80, 46, 14))
        self.update_health()

    def update_health(self,
                      health_value: int = None) -> None:

        if isinstance(health_value, int):
            self.current_health = health_value

        self.text_surf.fill(Resource.data["colors"][2])
        text = self.FONT.render(f"{self.current_health}/{self.max_health}", False, Resource.data["colors"][1])
        rect = text.get_rect()
        rect.center = 23, 5
        self.text_surf.blit(text, rect)
