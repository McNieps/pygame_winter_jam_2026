import pygame
import warnings

from typing import Callable

from isec.app import Resource
from isec.environment.scene.orthogonal_tilemap_scene import OrthogonalTilemapScene, OrthogonalTilemap
from isec.environment.base import Entity, Scene, Camera
from isec.environment.scene import EntityScene


class TMJScene(Scene):
    def __init__(self,
                 tmj_dict: dict,
                 fps: int | None,
                 surface: pygame.Surface = None,
                 camera: Camera = None,
                 objects_blueprint: dict[str, Callable[[tuple[int, int]], Entity]] = None) -> None:

        super().__init__(surface=surface, camera=camera)

        self.fps = fps

        if objects_blueprint is None:
            objects_blueprint = {}

        self.tmj_dict = tmj_dict
        self.sub_scenes: list[Scene] = []
        self.entity_scene: EntityScene | None = None
        self.load_scene(objects_blueprint)

    def load_scene(self, objects_blueprint: dict[str, Callable[[tuple[int, int]], Entity]] = None):
        # load tilemap values
        terrain_surf = ""
        objects_gid_mapping: dict[int, Callable[[tuple[int, int]], Entity]] = {}

        for tileset_dict in self.tmj_dict["tilesets"]:
            if tileset_dict["name"] == "terrain":
                terrain_surf = Resource.image
                for sub_folder in tileset_dict["image"].split("image")[-1].split(".png")[0].split("/"):
                    if sub_folder != "":
                        terrain_surf = terrain_surf[sub_folder]

            if tileset_dict["name"] == "objects":
                tileset_base_id = tileset_dict["firstgid"]
                for tile in tileset_dict["tiles"]:
                    try:
                        objects_gid_mapping[tile["id"]+tileset_base_id] = objects_blueprint[tile["type"]]
                    except KeyError:
                        if "type" in tile:
                            err_msg = f"Object type {tile['type']} not found in objects_blueprint."
                            warnings.warn(err_msg)

                        else:
                            err_msg = f"Object type not found in tile id={tile['id']}."
                            warnings.warn(err_msg)

        # generating scenes
        for layer in self.tmj_dict["layers"]:
            if layer["type"] == "tilelayer":
                tilemap_size = layer["width"], layer["height"]
                tilemap_array = [layer["data"][i:i + tilemap_size[0]]
                                 for i in range(0, len(layer["data"]), tilemap_size[0])]

                # get random tileset
                tile_size = self.tmj_dict["tilesets"][0]["tilewidth"]

                tilemap = OrthogonalTilemapScene(OrthogonalTilemap(tilemap_array,
                                                                   terrain_surf,
                                                                   tile_size,
                                                                   layer.get("parallaxx", 1)),
                                                 surface=self.surface,
                                                 camera=self.camera)

                self.sub_scenes.append(tilemap)

            elif layer["type"] == "objectgroup":
                entity_scene = EntityScene(self.fps)
                self.entity_scene = entity_scene
                self.sub_scenes.append(entity_scene)

                for obj in layer["objects"]:
                    if "gid" not in obj or obj["gid"] not in objects_gid_mapping:
                        continue

                    entity = objects_gid_mapping[obj["gid"]]((obj["x"], obj["y"]))
                    entity_scene.add_entities(entity)

    def update(self,
               delta: float) -> None:
        self.entity_scene.update(delta)

    def render(self,
               camera: Camera = None):

        for scene in self.sub_scenes:
            scene.render(self.camera)
