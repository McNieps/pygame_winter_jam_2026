import pygame
from typing import List, Optional

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
    def __init__(self, map_name: str) -> None:
        super().__init__()
        self.map_name = map_name
        self.drag = False
        self.bg_color = Resource.data["colors"][0]
        self.camera = Camera()
        self.landmark_info = LandmarkInfo(None)
        self.landmarks: List[List[Landmark]] = []

        # Register event handlers
        self.event_handler.register_callback("click", "down", self._start_click)
        self.event_handler.register_callback("click", "up", self._stop_click)

        # Load and build map data
        self._load_map_data()
        self._create_scenes()

    def _load_map_data(self) -> None:
        """Extract tile and passage data from resources and build the route graph."""
        map_data = Resource.data["maps"][self.map_name]
        layers = map_data["layers"]

        # Assume first layer is tilemap, second is passage (robustness could be improved)
        tile_layer = layers[0]
        passage_layer = layers[1]

        # Build tilemap array
        tile_data = tile_layer["data"]
        width = tile_layer["width"]
        self.tilemap_array = [
            tile_data[i:i + width] for i in range(0, len(tile_data), width)
        ]

        # Build passage points
        passage_points = []
        for obj in passage_layer["objects"]:
            # Extract properties (assumes first property contains number of landmarks)
            n_landmarks = obj["properties"][0]["value"] if obj["properties"] else 1
            passage_points.append(
                PassagePoint(x=obj["x"], y=obj["y"], n_landmarks=n_landmarks)
            )

        # Build route graph
        self.route = ConcreteRoute(passage_points=passage_points)
        self.route.build()

    def _create_scenes(self) -> None:
        """Create all rendering scenes: tilemap, landmarks, connections, UI."""
        self._create_tilemap_scene()
        self._create_landmarks_and_connections()
        self._create_ui_scene()

    def _create_tilemap_scene(self) -> None:
        """Set up the orthogonal tilemap scene."""
        tileset = Resource.image["tilesets"]["tileset_snow_forest"]
        tilemap = OrthogonalTilemap(
            self.tilemap_array,
            tileset=tileset,
            tile_size=self.TILE_SIZE
        )
        self.tilemap_scene = OrthogonalTilemapScene(tilemap, camera=self.camera)

    def _create_landmarks_and_connections(self) -> None:
        """Instantiate landmarks and their connections based on the route graph."""
        self.landmarks_scene = EntityScene(self.TARGET_FPS, camera=self.camera)
        self.landmarks = []

        # Create landmarks
        for col, layer in enumerate(self.route.placed_landmarks):
            landmark_column = []
            for landmark_desc in layer:
                pos = pygame.math.Vector2(landmark_desc.x, landmark_desc.y)
                landmark = Village(pos)
                landmark_column.append(landmark)
                self.landmarks_scene.add_entities(landmark)
            self.landmarks.append(landmark_column)

        # Create connections
        for col_i, row in enumerate(self.route.graph.columns):
            for row_i, node in enumerate(row):
                current = self.landmarks[col_i][row_i]
                for dest_col, dest_row in node.destinations:
                    connection = LandmarkConnexion(
                        current,
                        self.landmarks[dest_col][dest_row]
                    )
                    self.landmarks_scene.add_entities(connection)

    def _create_ui_scene(self) -> None:
        """Set up the UI scene (landmark info panel)."""
        self.ui_scene = EntityScene(
            self.TARGET_FPS,
            camera=self.camera,
            entities=[self.landmark_info]
        )

    # --------------------------------------------------------------------------
    # BaseInstance overrides
    # --------------------------------------------------------------------------

    async def setup(self) -> None:
        """Async setup (unused but required by base class)."""
        pass

    async def loop(self) -> None:
        """Main game loop: handle input, update, render."""
        self._handle_drag()
        self.window.fill(self.bg_color)
        self._update()
        self._render()

    # --------------------------------------------------------------------------
    # Input handling
    # --------------------------------------------------------------------------

    async def _start_click(self) -> None:
        """Handle mouse button down: check landmark click or start drag."""
        cursor_world = self.event_handler.mouse_pos + self.camera

        for entity in self.landmarks_scene.entities:
            if isinstance(entity, Landmark) and entity.rect.collidepoint(*cursor_world):
                self.landmark_info.focus(entity)
                return

        # No landmark clicked → start dragging
        self.landmark_info.unfocus()
        self.drag = True

    async def _stop_click(self) -> None:
        """Handle mouse button up: stop dragging."""
        self.drag = False

    def _handle_drag(self) -> None:
        """Update camera position while dragging, clamped to map bounds."""
        if not self.drag:
            return

        # Pre‑compute map boundaries (cache after first access)
        if not hasattr(self, "_map_max_x"):
            tilemap = self.tilemap_scene.tilemap
            self._map_max_x = tilemap.width * tilemap.tile_size - self.window.width
            self._map_max_y = tilemap.height * tilemap.tile_size - self.window.height

        self.camera -= pygame.math.Vector2(self.event_handler.mouse_rel)
        self.camera.x = max(0.0, min(self._map_max_x, self.camera.x))
        self.camera.y = max(0.0, min(self._map_max_y, self.camera.y))

    # --------------------------------------------------------------------------
    # Update and render
    # --------------------------------------------------------------------------

    def _update(self) -> None:
        """Update all scenes."""
        self.ui_scene.update(self.delta)

    def _render(self) -> None:
        """Render all scenes in order."""
        self.tilemap_scene.render()
        self.landmarks_scene.render()
        self.ui_scene.render()