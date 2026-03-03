import math
import pygame

from isec.environment.base import Entity, Camera, RenderingTechniques, IsometricTilemap
from isec.environment.scene.entity_scene import EntityScene


class IsometricEntityScene(EntityScene):
    def __init__(self,
                 fps: int,
                 tilemap: IsometricTilemap,
                 surface: pygame.Surface = None,
                 entities: list[Entity] = None,
                 camera: Camera = None) -> None:

        super().__init__(fps=fps,
                         surface=surface,
                         entities=entities,
                         camera=camera)

        self.tilemap = tilemap
        self._iso_half_tile = tilemap.tile_size[0]//2, tilemap.tile_size[1]//2
        self._iso_max_row_slots = sum(tilemap.size)
        print(self._iso_max_row_slots)
        # ^ equal to numbers of rows + 1, because it's represent the space BETWEEN rows (which are lines)

        self._iso_z_sort = [list() for _ in range(self._iso_max_row_slots+1)]

    def z_sort(self) -> None:
        self._iso_z_sort = [list() for _ in range(self._iso_max_row_slots+1)]

        for entity in self.entities:
            entity.row = entity.position.x + entity.position.y
            entity.col = entity.position.x - entity.position.y
            list_index = max(min(math.floor(entity.row), self._iso_max_row_slots), 0)
            self._iso_z_sort[list_index].append(entity)

        for row_slot in self._iso_z_sort:
            row_slot.sort(key=lambda ent: ent.row)

    def render_iso_range(self,
                         row_min: int | None,
                         row_max: int | None,
                         camera: Camera = None):

        if camera is None:
            camera = self.camera

        camera_pos = pygame.Vector2(math.floor(camera.position.x),
                                    math.floor(camera.position.y))

        for row_slot in self._iso_z_sort[row_min:row_max]:
            for entity in row_slot:
                x = math.floor(entity.col * self._iso_half_tile[0] - camera_pos[0])
                y = math.floor(entity.row * self._iso_half_tile[1] - camera_pos[1])-entity.sprite.rect.height/2
                RenderingTechniques.forced(entity.sprite, self.surface, 0, (x, y), 0)  # NOQA
