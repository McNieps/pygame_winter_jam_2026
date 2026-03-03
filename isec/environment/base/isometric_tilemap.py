import pygame


class IsometricTilemap:
    EMPTY_TILE = -1

    def __init__(self,
                 tilemap_array: list[list[int]],
                 tileset: dict[int, pygame.Surface | None],
                 heightmap_array: list[list[int]] = None,
                 tile_size: tuple[int, int] = None) -> None:
        """
        A class that represent an ISOMETRIC tilemap.

        :param tilemap_array: A 2D array of integers that represent the tiles of the map.
        :param heightmap_array: A 2D array of integers that represent the height of each tile (in px).
        :param tileset: A dictionary that maps tile_id (integers) with their corresponding tile surface (pg surface).
        :param tile_size: The size of the tiles in pixels.
        """

        if tile_size is None:
            tile_size = self._tile_size_from_tileset(tileset)

        if heightmap_array is None:
            heightmap_array = [[0 for _i in range(len(tilemap_array[0]))] for _j in range(len(tilemap_array))]

        self.tilemap_array = tilemap_array
        self.heightmap_array = heightmap_array
        self.tileset = tileset
        self.tile_size = tile_size
        self.min_col = self.height - 1
        self.max_col = self.width - 1
        self.min_row = 0
        self.max_row = self.width + self.height - 2
        self._check_tileset_validity(self.tilemap_array, self.tileset)

    @staticmethod
    def _check_tileset_validity(tilemap_array: list[list[int]],
                                tileset: dict[int: pygame.Surface | None]) -> bool:
        """A function that check if the tileset is valid."""

        return all(tile in tileset
                   for row in tilemap_array
                   for tile in row)

    @staticmethod
    def _tile_size_from_tileset(tileset) -> tuple[int, int]:
        """A function that return the tile size from a constructed tileset."""
        return tileset[0].get_width(), tileset[0].get_width()/2

    def create_collision_map(self,
                             collision_tiles: list[int]) -> list[list[bool]]:
        """
        Function that return a collision map where every tile adjacent to void tiles is True and False otherwise.

        :param collision_tiles: A list of integers that represent the tiles that are collidable.
        """

        if len(collision_tiles) == 0:
            raise ValueError("The list of collision tiles must not be empty.")

        collision_map = []

        for y, row in enumerate(self.tilemap_array):
            collision_map.append([False] * len(row))

            for x, tile in enumerate(row):
                if tile in collision_tiles:
                    collision_map[y][x] = True

        return collision_map

    @property
    def size(self):
        return len(self.tilemap_array[0]), len(self.tilemap_array)

    @property
    def width(self):
        return len(self.tilemap_array[0])

    @property
    def height(self):
        return len(self.tilemap_array)

    def __getitem__(self, item):
        return self.tilemap_array[item]
