import pygame

from isec.environment.base.camera import Camera
from isec.environment.base.position import Position
from isec.environment.base.sprite import Sprite


class Entity:
    def __init__(self,
                 position: pygame.Vector2 | tuple[float, float],
                 sprite: Sprite) -> None:

        self.to_delete: bool = False
        self.sprite: Sprite = sprite

        if isinstance(position, Position):
            self.position: Position = position
        else:
            self.position: Position = Position(position)

    def update(self,
               delta: float) -> None:

        self.position.update_components(delta)
        self.sprite.update(delta)

    def render(self,
               camera: Camera,
               surface: pygame.Surface,
               rect: pygame.Rect) -> None:

        vec = camera.get_offset(self.position)
        self.sprite.render(surface, rect, vec, self.position.angle)

    def destroy(self) -> None:

        self.to_delete = True
