from isec.instance.base_instance import BaseInstance
from isec.app import Resource


from isec.environment import Sprite, Entity, EntityScene
from isec.environment.scene import OrthogonalTilemapScene
from isec.environment.base import OrthogonalTilemap


class WorldMapInstance(BaseInstance):
    def __init__(self):
        super().__init__()

        self.bg_color = Resource.data["colors"][0]
        self.tilemap = OrthogonalTilemapScene(OrthogonalTilemap(Resource.data["map"]["map_test"],
                                                                tileset=Resource.image["tilesets"]["tileset_snow_forest"],
                                                                tile_size=8))

    async def setup(self) -> None:
        pass

    async def loop(self):
        self.window.fill(self.bg_color)
        self.tilemap.render()
