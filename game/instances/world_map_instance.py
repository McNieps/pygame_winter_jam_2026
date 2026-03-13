import pygame

from isec.app import Resource
from isec.instance.base_instance import BaseInstance

from isec.environment.scene import OrthogonalTilemapScene, EntityScene
from isec.environment.base import OrthogonalTilemap, Camera

from game.entities.landmarks.landmark import Landmark
from game.entities.landmarks.village import Village
from game.entities.landmarks.landmark_connexion import LandmarkConnexion
from game.entities.ui.landmark_info import LandmarkInfo
from game.world_gen import ConcreteRoute, PassagePoint


class WorldMapInstance(BaseInstance):
    def __init__(self, map_name: str):
        super().__init__()
        self.map_name = map_name
        self.drag = False
        self.event_handler.register_callback("click", "down", self.start_click)
        self.event_handler.register_callback("click", "up", self.stop_click)
        self.bg_color = Resource.data["colors"][0]
        self.camera = Camera()
        self.landmark_info = LandmarkInfo(None)
        self.landmarks: list[list[Landmark]] = []

        tilemap_layer, passage_layer = Resource.data["maps"][map_name]["layers"][:2]
        tilemap_array = [tilemap_layer["data"][i:i + tilemap_layer["width"]] for i in range(0, len(tilemap_layer["data"]), tilemap_layer["width"])]

        passage_points = []
        for passage_point in passage_layer["objects"]:
            passage_points.append(
                PassagePoint(x=passage_point["x"], y=passage_point["y"], n_landmarks=passage_point["properties"][0]["value"])
            )

        route = ConcreteRoute(passage_points=passage_points)
        route.build()
        self.tilemap_scene  = OrthogonalTilemapScene(
            OrthogonalTilemap(
                tilemap_array,
                tileset=Resource.image["tilesets"]["tileset_snow_forest"],
                tile_size=8),
            camera=self.camera)

        self.landmarks_scene = EntityScene(60,
                                           camera=self.camera)
                                           # entities=[Village(pygame.math.Vector2(pp.x, pp.y)) for pp in passage_points])

        self.landmarks = []
        for layer in route.placed_landmarks:
            landmark_col = []
            for landmark_desc in layer:
                landmark = Village(pygame.math.Vector2(landmark_desc.x, landmark_desc.y))
                landmark_col.append(landmark)
                self.landmarks_scene.add_entities(landmark)
            self.landmarks.append(landmark_col)

        for col_i, row in enumerate(route.graph.columns):
            for row_i, node in enumerate(row):
                current_landmark = self.landmarks[col_i][row_i]
                for dest_col, dest_row in node.destinations:
                    self.landmarks_scene.add_entities(LandmarkConnexion(current_landmark, self.landmarks[dest_col][dest_row]))

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
            if not isinstance(landmark, Landmark):
                continue

            if landmark.rect.collidepoint(*cursor_world_pos):
                self.landmark_info.focus(landmark)
                return

        self.landmark_info.unfocus()
        self.drag = True

    async def stop_click(self):
        self.drag = False
