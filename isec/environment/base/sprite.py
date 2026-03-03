import typing
import pygame

from collections.abc import Iterable

from isec.objects.cached_surface import CachedSurface
from isec.environment.base.rendering_techniques import RenderingTechniques


class Sprite:
    __slots__ = ["surface",
                 "rect",
                 # "max_rect",
                 "effective_surf",
                 "effective_rect",
                 "_rendering_technique",
                 "blit_flag",
                 "displayed"]

    def __init__(self,
                 surface: pygame.Surface,
                 rendering_technique: RenderingTechniques.TYPING = "static",
                 blit_flag: int = 0,
                 position_anchor: tuple[int, int] | str = "center") -> None:

        self.displayed: bool = True
        self.surface = surface
        self.rect = self.surface.get_rect()
        # self.max_rect = self.rect.copy()
        # self.max_rect.width = math.ceil(self.max_rect.width * math.sqrt(2))
        # self.max_rect.height = math.ceil(self.max_rect.height * math.sqrt(2))
        # self.max_rect.center = 0, 0

        # lmao
        match position_anchor:
            case x, y: self.rect.topleft = -x, -y
            case "center": self.rect.center = 0, 0
            case "topleft": self.rect.topleft = 0, 0
            case "top": self.rect.midtop = 0, 0
            case "topright": self.rect.topright = 0, 0
            case "right": self.rect.midright = 0, 0
            case "bottomright": self.rect.bottomright = 0, 0
            case "bottom": self.rect.midbottom = 0, 0
            case "bottomleft": self.rect.bottomleft = 0, 0
            case "left": self.rect.midleft = 0, 0
            case _: raise Exception("position anchor is not valid")

        # self.rect.midbottom = 0, 0   # REPLACED self.rect.center WITH self.rect.midbottom

        self.effective_surf = self.surface
        self.effective_rect = self.rect

        self._rendering_technique = RenderingTechniques.static
        self.set_rendering_technique(rendering_technique)
        self.blit_flag = blit_flag

    def update(self,
               delta: float) -> None:

        pass

    def set_rendering_technique(self,
                                rendering_technique: typing.Literal["static", "rotated", "cached"]) -> None:

        if rendering_technique == "static":
            self._rendering_technique = RenderingTechniques.static

        elif rendering_technique == "rotated":
            self._rendering_technique = RenderingTechniques.rotated

        elif rendering_technique == "cached":
            if not isinstance(self.surface, CachedSurface):
                raise ValueError("Cached rendering technique requires cached surface.")
            self._rendering_technique = RenderingTechniques.cached

        elif rendering_technique == "optimized_static":
            self._rendering_technique = RenderingTechniques.optimized_static

        else:
            raise ValueError("Invalid rendering technique.")

    def render(self,
               destination: pygame.Surface,
               destination_rect: pygame.Rect,
               offset: Iterable,
               angle: float) -> None:

        if not self.displayed:
            return

        self._rendering_technique(self,
                                  destination,
                                  destination_rect,
                                  offset,
                                  angle)

    def switch_state(self,
                     state: str) -> None:
        if state not in self.surface:
            err_msg = f"Only StateSprite support switch_state method"
            raise ValueError(err_msg)

    def flip(self,
             x: bool = True,
             y: bool = False) -> None:
        print("TRIED TO FLIP")
        self.surface = pygame.transform.flip(self.surface, x, y)
