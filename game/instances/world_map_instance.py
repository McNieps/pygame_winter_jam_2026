import pygame
from typing import List

from game.entities.ui.inventory_button import InventoryButton
from game.instances.inventory_instance import InventoryInstance
from game.instances.combat_instance import CombatInstance
from game.instances.shop_instance import ShopInstance
from isec.app import Resource
from isec.instance.base_instance import BaseInstance
from isec.environment.scene import OrthogonalTilemapScene, EntityScene
from isec.environment.base import OrthogonalTilemap, Camera

from game.battle_engine.models import Team, Weapon
from game.entities.landmarks import landmark_dict, Landmark
from game.entities.ui.landmark_connexion import LandmarkConnexion
from game.entities.ui.landmark_info import LandmarkInfo
from game.world_gen import MapGenerator
from game.entities.combat.back_snow_layer import BackSnowLayer as FrontSnowLayer
from game.entities.player import Player



team_a = Team(
    name="Team A", hp=100, max_hp=100,
    weapons=[Weapon(name="Reactive Blade", base_damage=100, cooldown_ticks_max=8, modifiers=[], icon="dagger")],
)
team_b = Team(
    name="Team B", hp=100, max_hp=100,
    weapons=[Weapon(name="Predator Axe", base_damage=12, cooldown_ticks_max=5, modifiers=[], icon="dagger"),
             Weapon(name="Predator Axe", base_damage=12, cooldown_ticks_max=5, modifiers=[], icon="dagger"),
             Weapon(name="Predator Axe", base_damage=12, cooldown_ticks_max=5, modifiers=[], icon="dagger")],
)


class WorldMapInstance(BaseInstance):
    def __init__(self, map_name: str) -> None:
        super().__init__()
        self.map_name = map_name
        self.drag = False
        self.bg_color = Resource.data["colors"][0]
        self.camera = Camera()
        self.landmarks: List[List[Landmark]] = []
        self.map_layout = MapGenerator()

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
        landmarks_per_step = []
        for obj in passage_layer["objects"]:
            n_landmarks = obj["properties"][0]["value"] if obj["properties"] else 1
            landmarks_per_step.append(n_landmarks)
            passage_points.append((obj["x"], obj["y"]))

        self.map_layout.generate_structure(len(landmarks_per_step), landmarks_per_step)
        self.map_layout.generate_map_layout(passage_points)
        self.map_layout.affect_node_type()

    def _create_scenes(self) -> None:
        self._create_tilemap_scene()
        self._create_landmarks_and_connections()
        self._create_ui_scene()

    def _create_tilemap_scene(self) -> None:
        tileset = Resource.image["tilesets"]["tileset_snow_forest"]
        tilemap = OrthogonalTilemap(
            self.tilemap_array,
            tileset=tileset,
            tile_size=8
        )
        self.tilemap_scene = OrthogonalTilemapScene(tilemap, camera=self.camera)

    def _create_landmarks_and_connections(self) -> None:
        """Instantiate landmarks and their connections based on the route graph."""
        self.landmarks_scene = EntityScene(self.fps, camera=self.camera)
        self.landmarks = []

        # Create landmarks
        for layer_index, layer in enumerate(self.map_layout.map):
            landmark_column = []
            for node_index, landmark_node in enumerate(layer):
                pos = pygame.math.Vector2(landmark_node.position)
                landmark = landmark_dict[landmark_node.name](pos, (layer_index, node_index))
                landmark_column.append(landmark)
                self.landmarks_scene.add_entities(landmark)
            self.landmarks.append(landmark_column)

        # Create connections
        for layer_i, layer in enumerate(self.map_layout.map):
            for node_i, node in enumerate(layer):
                current = self.landmarks[layer_i][node_i]
                for dest_col, dest_row in node.connections:
                    connection = LandmarkConnexion(
                        current,
                        self.landmarks[dest_col][dest_row]
                    )
                    self.landmarks_scene.add_entities(connection)

    def _create_ui_scene(self) -> None:
        """Set up the UI scene (landmark info panel)."""
        self.player = Player(self.landmarks[0][0])
        self.landmark_info = LandmarkInfo(self.player, self.map_layout)
        self.inventory_button = InventoryButton()
        self.ui_scene = EntityScene(
            self.fps,
            camera=self.camera,
            entities=[self.player, self.landmark_info, self.landmark_info.go_button]
        )
        self.snow_layer = FrontSnowLayer()
        self.snow_front_scene = EntityScene(
            self.fps,
            entities=[self.snow_layer, self.inventory_button]
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
        await self._handle_player_movement()

    # --------------------------------------------------------------------------
    # Input handling
    # --------------------------------------------------------------------------

    async def _start_click(self) -> None:
        """Handle mouse button down: check landmark click or start drag."""
        cursor_world = self.event_handler.mouse_pos + self.camera

        if self.inventory_button.rect.collidepoint(*self.event_handler.mouse_pos):
            self.landmark_info.unfocus()
            await InventoryInstance().execute()
            return
        if self.landmark_info.go_button.active and self.landmark_info.go_button.rect.collidepoint(*cursor_world):
            self.player.move(self.landmark_info.landmark_focused)
            self.landmark_info.unfocus()
            Resource.sound["snow"].play()
            return

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

        initial_cam_pos = self.camera.copy()

        self.camera -= pygame.math.Vector2(self.event_handler.mouse_rel)
        self.camera.x = max(0.0, min(self._map_max_x, self.camera.x))
        self.camera.y = max(0.0, min(self._map_max_y, self.camera.y))

        self.snow_layer.scroll(*(initial_cam_pos-self.camera))

    # --------------------------------------------------------------------------
    # Update and render
    # --------------------------------------------------------------------------

    def _update(self) -> None:
        """Update all scenes."""
        self.ui_scene.update(self.delta)
        self.snow_front_scene.update(self.delta)

    def _render(self) -> None:
        """Render all scenes in order."""
        self.tilemap_scene.render()
        self.landmarks_scene.render()
        self.ui_scene.render()
        self.snow_front_scene.render()

    async def _handle_player_movement(self):
        if self.player.movement_over:
            await CombatInstance(team_a, team_b).execute()

        self.player.movement_over = False
