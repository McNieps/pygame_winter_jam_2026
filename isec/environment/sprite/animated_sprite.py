import pygame

from isec.environment.base import Sprite, RenderingTechniques


class AnimatedSprite(Sprite):
    def __init__(self,
                 surfaces: list[pygame.Surface],
                 frames_duration: list[float],
                 loop_origin: int = None,
                 rendering_technique: RenderingTechniques.TYPING = "static",
                 blit_flag: int = 0,
                 position_anchor: tuple[int, int] | str = "center") -> None:

        if len(surfaces) == 0:
            raise ValueError("Length of surfaces must be greater than 0.")

        if len(surfaces) != len(frames_duration):
            raise ValueError("Length of surfaces and frames_duration must be equal.")

        if not all(isinstance(duration, (int | float)) for duration in frames_duration):
            raise ValueError("All frames_duration must be int or float.")

        super().__init__(surface=surfaces[0],
                         rendering_technique=rendering_technique,
                         blit_flag=blit_flag,
                         position_anchor=position_anchor)

        self.surfaces: list[pygame.Surface] = surfaces
        self.frames_duration: list[float] = frames_duration
        self.loop_origin: int | None = loop_origin

        self._current_frame: int = 0
        self._current_duration: float = 0.0

    def update(self,
               delta: float) -> None:

        self._current_duration += delta
        if self._current_duration >= self.frames_duration[self._current_frame]:
            self._current_duration -= self.frames_duration[self._current_frame]
            self._current_frame += 1

            if self._current_frame >= len(self.surfaces):
                if self.loop_origin is not None:
                    self._current_frame = self.loop_origin
                else:
                    self._current_frame = len(self.surfaces) - 1

            while self.frames_duration[self._current_frame] == 0:
                self._current_frame += 1
                if self._current_frame >= len(self.surfaces):
                    if self.loop_origin is not None:
                        self._current_frame = self.loop_origin
                    else:
                        self._current_frame = len(self.surfaces) - 1
                        break

            self.surface = self.surfaces[self._current_frame]

    def reselect_surface(self) -> None:
        self.surface = self.surfaces[self._current_frame]

    def reset_animation(self, frame: int = 0) -> None:
        self._current_frame: int = frame
        self._current_duration: float = 0.0

    def render(self,
               destination: pygame.Surface,
               destination_rect: pygame.Rect,
               offset: tuple[int, int],
               angle: float) -> None:

        super().render(destination, destination_rect, offset, angle)
