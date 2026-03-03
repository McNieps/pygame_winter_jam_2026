import pygame
import pymunk
import pymunk.autogeometry

from typing import Self, Type

from isec.environment.base import Entity, Sprite, OrthogonalTilemap
from isec.environment.sprite import PymunkSprite
from isec.environment.position.pymunk_pos import PymunkPos, PymunkShapeInfo


class TerrainCollision(Entity):
    SHAPES_RADIUS = 0.5

    def __init__(self,
                 polygon: list[tuple],
                 shape_info: Type[PymunkShapeInfo],
                 show_collisions: bool = False) -> None:

        position = PymunkPos(body_type="STATIC",
                             default_shape_info=shape_info)

        position.add_shape(pymunk.Poly(body=position.body,
                                       vertices=polygon,
                                       radius=self.SHAPES_RADIUS))

        # position.add_to_space()

        if show_collisions:
            sprite = PymunkSprite(position)
        else:
            sprite = Sprite(pygame.Surface((0, 0), pygame.SRCALPHA))

        super().__init__(position=position,
                         sprite=sprite)

    @classmethod
    def from_collision_map(cls,
                           collision_map: list[list[bool]],
                           tile_size: int,
                           shape_info: Type[PymunkShapeInfo] = None,
                           show_collisions: bool = False) -> list[Self]:

        entities = []

        # prepare collision map
        for y in range(len(collision_map)):
            for x in range(len(collision_map[0])):
                if x == 0 or y == 0 or x == len(collision_map[0])-1 or y == len(collision_map)-1:
                    collision_map[y][x] = False

        for polygon in cls._decompose_collision_map_into_polygons(collision_map, tile_size):
            new_body = cls(polygon=polygon,
                           shape_info=shape_info,
                           show_collisions=show_collisions)

            entities.append(new_body)

        return entities

    @staticmethod
    def _decompose_collision_map_into_polygons(collision_map: list[list[bool]],
                                               tile_size: int) -> list[list[tuple]]:
        """Edges must be not collidable! It's cause by pymunk.autogeometry.march_hard and march_soft functions."""

        def sample_function(point):
            return collision_map[round(point[1])][round(point[0])]

        bounding_box = pymunk.BB(len(collision_map[0])-1, len(collision_map)-1)

        raw_polyset = pymunk.autogeometry.march_hard(bounding_box,
                                                     len(collision_map[0]),
                                                     len(collision_map),
                                                     0,
                                                     sample_function)

        sized_polyset = []

        for raw_polygon in raw_polyset:
            sized_polygon = []
            for raw_vertices in raw_polygon:
                sized_polygon.append((raw_vertices.x * tile_size + tile_size/2,
                                      raw_vertices.y * tile_size + tile_size/2))

            sized_polyset.append(sized_polygon)

        concave_polyset = []

        for sized_polygon in sized_polyset:
            try:
                fixed_polyset = pymunk.autogeometry.convex_decomposition(sized_polygon, 0)

            except AssertionError:
                sized_polygon.reverse()
                fixed_polyset = pymunk.autogeometry.convex_decomposition(sized_polygon, 0)

            for fixed_polygon in fixed_polyset:
                concave_polyset.append(fixed_polygon)

        return concave_polyset

    @classmethod
    def from_tilemap(cls,
                     tilemap: OrthogonalTilemap,
                     shape_info: Type[PymunkShapeInfo] = None,
                     show_collisions: bool = False) -> list[Self]:

        return cls.from_collision_map([[i != -1 for i in j] for j in tilemap.tilemap_array],
                                      tilemap.tile_size,
                                      shape_info,
                                      show_collisions)



