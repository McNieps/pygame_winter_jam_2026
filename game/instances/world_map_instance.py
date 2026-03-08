import pygame

from isec.environment import EntityScene
from isec.instance.base_instance import BaseInstance
from isec.app import Resource


from isec.environment.scene import OrthogonalTilemapScene
from isec.environment.base import OrthogonalTilemap, Camera

from game.entities.landmarks.village import Village
from game.entities.ui.landmark_info import LandmarkInfo


class WorldMapInstance(BaseInstance):
    def __init__(self):
        super().__init__()
        self.drag = False
        self.event_handler.register_callback("click", "down", self.start_click)
        self.event_handler.register_callback("click", "up", self.stop_click)
        self.bg_color = Resource.data["colors"][0]
        self.camera = Camera()
        self.landmark_info = LandmarkInfo(None)

        self.tilemap_scene  = OrthogonalTilemapScene(OrthogonalTilemap(Resource.data["map"]["map_test"],
                                                                tileset=Resource.image["tilesets"]["tileset_snow_forest"],
                                                                tile_size=8),
                                                     camera=self.camera)

        self.landmarks_scene = EntityScene(60,
                                           camera=self.camera,
                                           entities=[Village(pygame.math.Vector2(100, 100))])

        self.ui_scene = EntityScene(60,
                                    camera=self.camera,
                                    entities=[self.landmark_info])

    async def setup(self) -> None:
        pass

    async def loop(self):
        if self.drag:
            max_x = self.tilemap_scene.tilemap.width * self.tilemap_scene.tilemap.tile_size - self.window.width
            max_y = self.tilemap_scene.tilemap.height * self.tilemap_scene.tilemap.tile_size - self.window.height
            self.tilemap_scene.camera -= pygame.math.Vector2(self.event_handler.mouse_rel)
            self.tilemap_scene.camera.x = max(min(max_x, self.tilemap_scene.camera.x), 0.0)
            self.tilemap_scene.camera.y = max(min(max_y, self.tilemap_scene.camera.y), 0.0)

        self.window.fill(self.bg_color)

        self.ui_scene.update(self.delta)

        self.tilemap_scene.render()
        self.landmarks_scene.render()
        self.ui_scene.render()

    async def start_click(self):
        cursor_world_pos = self.event_handler.mouse_pos + self.camera
        for landmark in self.landmarks_scene.entities:
            if landmark.rect.collidepoint(*cursor_world_pos):
                self.landmark_info.focus(landmark)
                return

        self.landmark_info.unfocus()
        self.drag = True

    async def stop_click(self):
        self.drag = False
        self.clicked_entity = None
