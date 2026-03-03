import pygame
# import pymunk

from isec.environment.base.camera import Camera
from isec.environment.base import Entity, Scene
# from isec.environment.position import PymunkPos


class EntityScene(Scene):
    def __init__(self,
                 fps: int,
                 surface: pygame.Surface = None,
                 entities: list[Entity] = None,
                 camera: Camera = None) -> None:

        super().__init__(surface, camera)

        if entities is None:
            entities = []
        self.entities = entities

        self.avg_delta = 1 / fps
#        self._space = pymunk.Space()

    def add_entities(self,
                     *entities: Entity) -> None:
        """obvious."""
#         for entity in entities:
#             if isinstance(entity.position, PymunkPos):
#                 entity.position.add_to_space(self._space)

        self.entities.extend([entity for entity in entities
                              if entity not in self.entities])

    def get_entity_by_name(self,
                           name: str) -> Entity | None:
        """Will return the first entity found with the given name."""

        for entity in self.entities:
            if entity.__class__.__name__ == name:
                return entity

        return None

    def remove_entities(self,
                        *entities: Entity) -> None:
        """Removes the given entities from the scene."""

        for entity in entities:
            if entity not in self.entities:
                continue

#            if isinstance(entity.position, PymunkPos):
#                entity.position.remove_from_space()

            self.entities.remove(entity)

    def remove_entities_by_name(self,
                                name: str) -> None:
        """Removes all entities with the given name from the scene."""
        for entity in self.entities:
            if entity.__class__.__name__ == name:
                self.remove_entities(entity)

    def update(self,
               delta: float) -> None:
        """Updates all entities in the scene."""
        for entity in self.entities:
            entity.update(delta)

        for entity in reversed(self.entities):
            if entity.to_delete:
                self.remove_entities(entity)

#        self.space.step(self.avg_delta)

    def z_sort(self):
        """Sorts the entities by their y position
        Used for rendering purposes."""
        self.entities.sort(key=lambda entity: entity.position.y)

    def render(self,
               camera: Camera = None) -> None:
        """obvious."""
        if camera is None:
            camera = self.camera

        for entity in self.entities:
            entity.render(camera, self.surface, self.rect)

#    @property
#    def space(self) -> pymunk.Space:
#        return self._space
