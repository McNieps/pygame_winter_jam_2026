import pygame
import numpy
import math

from isec.environment.base import IsometricTilemap
from isec.environment.base.scene import Scene
from isec.environment.base.camera import Camera


class IsometricTilemapScene(Scene):
    def __init__(self,
                 tilemap: IsometricTilemap,
                 surface: pygame.Surface = None,
                 camera: Camera = None) -> None:

        super().__init__(surface, camera)
        self.tilemap = tilemap

    def renderable_rect(self,
                        camera: Camera = None) -> pygame.Rect:

        if camera is None:
            camera = self.camera

        tile_size = self.tilemap.tile_size
        camera_pos = pygame.Vector2(math.floor(camera.position.x),
                                    math.floor(camera.position.y))

        r_min = math.floor(camera_pos[1]/tile_size[1]*2)-4   # Need more work to take height into account
        r_max = math.ceil(self.surface.get_height()/tile_size[1]*2)+r_min+8
        c_min = math.floor(camera_pos[0]/tile_size[0]*2)-1
        c_max = math.ceil(self.surface.get_width()/tile_size[0]*2)+c_min+2+1

        return pygame.Rect((c_min, r_min), (c_max-c_min, r_max-r_min))

    def render_row(self,
                   row: int,
                   col_min: int,
                   col_max: int,
                   camera: Camera = None) -> None:

        if row < self.tilemap.min_row or row > self.tilemap.max_row:
            return

        if camera is None:
            camera = self.camera

        camera_pos = pygame.Vector2(math.floor(camera.position.x),
                                    math.floor(camera.position.y))
        tile_size = self.tilemap.tile_size

        for col in range(col_min, col_max):
            if (col + row) % 2 != 0:
                continue

            i = (row + col)//2
            j = (row - col)//2
            if i < 0 or j < 0 or i >= self.tilemap.width or j >= self.tilemap.height:
                continue

            tile_id = self.tilemap[j][i]
            if tile_id == self.tilemap.EMPTY_TILE:
                continue

            x = numpy.floor(col*tile_size[0]/2 - camera_pos[0] - tile_size[0]/2)
            y = numpy.floor(row*tile_size[1]/2 - camera_pos[1]) - self.tilemap.heightmap_array[j][i]

            # tile
            self.surface.blit(self.tilemap.tileset[tile_id], (x, y))

    def render(self,
               camera: Camera = None) -> None:

        if camera is None:
            camera = self.camera

        camera_pos = pygame.Vector2(math.floor(camera.position.x),
                                    math.floor(camera.position.y))
        tile_size = self.tilemap.tile_size
        renderable_rect = self.renderable_rect(camera)
        r_min, r_max = renderable_rect.top, renderable_rect.bottom
        c_min, c_max = renderable_rect.left, renderable_rect.right

        # r & c: row and column, i & j: tile pos in tilemap, x & y: tile pos in viewspace
        for r in range(r_min, r_max):
            for c in range(c_min, c_max):
                if (c + r) % 2 != 0:
                    continue

                i = (r + c)//2
                j = (r - c)//2

                if i < 0 or j < 0 or i >= self.tilemap.width or j >= self.tilemap.height:
                    continue

                tile_id = self.tilemap[j][i]
                if tile_id == self.tilemap.EMPTY_TILE:
                    continue

                x = numpy.floor(c*tile_size[0]/2 - camera_pos[0] - tile_size[0]/2)
                y = numpy.floor(r*tile_size[1]/2 - camera_pos[1] - tile_size[1]/2) - self.tilemap.heightmap_array[j][i]
                # tile
                self.surface.blit(self.tilemap.tileset[tile_id], (x, y))

        return

    def update(self,
               delta: float) -> None:
        pass
