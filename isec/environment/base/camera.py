import pygame


class Camera(pygame.math.Vector2):
    def __init__(self,
                 position: pygame.Vector2 | tuple[int, int] = (0, 0)) -> None:

        super().__init__(position)

    def get_offset(self,
                   position: pygame.Vector2) -> pygame.math.Vector2:

        return position//1 - self//1

    def get_coordinates_from_screen(self,
                                    screen_coordinates: pygame.math.Vector2 | tuple[float, float]) -> pygame.Vector2:

        return self + screen_coordinates
