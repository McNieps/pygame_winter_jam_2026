import pygame
# import pymunk

from collections.abc import Callable


class Position(pygame.Vector2):
    def __init__(self,
                 base_position: pygame.Vector2 | tuple[float, float] = (0, 0)):

        super().__init__(*base_position)
        self.vx = 0
        self.vy = 0
        self.damping = 0
        self.angle = 0
        self.angular_speed = 0
        self.angular_damping = 0

        self.components: dict[str, Callable[[float], None]] = {}

    def update_components(self,
                          delta: float) -> None:
        for component in self.components.values():
            component(delta)

    def add_linear_component(self,
                             vx: float,
                             vy: float,
                             damping: float = 1):
        self.vx = vx
        self.vy = vy
        self.damping = damping

        self.components["linear"] = self.update_linear_component

    def update_linear_component(self,
                                delta: float):
        self.vx *= self.damping ** delta
        self.vy *= self.damping ** delta
        self.x += self.vx * delta
        self.y += self.vy * delta

    def add_rotational_component(self,
                                 angle: float = 0,
                                 angular_speed: float = 0,
                                 angular_damping: float = 1):
        self.angle = angle
        self.angular_speed = angular_speed
        self.angular_damping = angular_damping

        self.components["rotational"] = self.update_rotational_component

    def update_rotational_component(self,
                                    delta: float):
        self.angular_speed *= self.angular_damping ** delta
        self.angle += self.angular_speed * delta
