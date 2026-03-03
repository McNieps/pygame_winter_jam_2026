import pygame

from typing import Self

from isec.app import Resource
from isec.environment.base import RenderingTechniques
from isec.environment.sprite.animated_sprite import AnimatedSprite


class StateSprite(AnimatedSprite):
    def __init__(self,
                 states_surfaces: dict[str, list[pygame.Surface]],
                 states_durations: dict[str, list[float]],
                 states_loop: dict[str, bool],
                 rendering_technique: RenderingTechniques.TYPING = "static",
                 blit_flag: int = 0,
                 position_anchor: tuple[int, int] | str = "center") -> None:

        if len(states_durations) == 0:
            raise ValueError("States durations dict is empty!")

        self.states_surfaces = states_surfaces
        self.states_durations = states_durations
        self.states_loop = states_loop
        self.current_state = list(self.states_durations.keys())[0]

        super().__init__(self.states_surfaces[self.current_state],
                         self.states_durations[self.current_state],
                         self.states_loop[self.current_state],
                         rendering_technique,
                         blit_flag,
                         position_anchor)

    def switch_state(self,
                     state_name: str) -> None:

        if state_name not in self.states_surfaces:
            err_msg = (f"{state_name} is not a valid state name. "
                       f"Only these states are available for this sprite: {list(self.states_surfaces.keys())}.")
            raise IndexError(err_msg)

        if state_name != self.current_state:
            self.reset_animation()

        self.current_state = state_name
        self.surfaces = self.states_surfaces[state_name]
        self.frames_duration = self.states_durations[state_name]
        self.loop_origin = self.states_loop[state_name]

    def flip(self,
             flip_x: bool = True,
             flip_y: bool = False) -> None:

        for surf_list in self.states_surfaces.values():
            for i, surface in enumerate(surf_list):
                surf_list[i] = pygame.transform.flip(surface, flip_x, flip_y)
        self.reselect_surface()

    @classmethod
    def create_from_directory(cls,
                              directory_path: str,
                              rendering_technique: RenderingTechniques.TYPING = "static",
                              blit_flag: int = 0,
                              position_anchor: tuple[int, int] | str = "center") -> Self:

        keys = directory_path.replace("\\", "/").rstrip("/").split("/")

        base_surfaces_dict = Resource.image
        base_states_dict = Resource.data["image"]

        for key in keys:
            base_surfaces_dict = base_surfaces_dict[key]
            base_states_dict = base_states_dict[key]

        base_states_dict = base_states_dict["state"]
        surfaces_dict = {}
        durations_dict = {}
        loop_dict = {}

        for state in base_states_dict:
            surfaces_dict[state] = []
            durations_dict[state] = []

            loop_dict[state] = base_states_dict[state].get("loop_origin", base_states_dict[state].get("loop", None))
            if type(loop_dict[state]) is bool:
                loop_dict[state] = 0 if loop_dict[state] else None

            for frame in base_states_dict[state]["frames"]:
                surfaces_dict[state].append(base_surfaces_dict[frame["image"]])
                durations_dict[state].append(frame["duration"])

        return cls(surfaces_dict,
                   durations_dict,
                   loop_dict,
                   rendering_technique,
                   blit_flag,
                   position_anchor)
