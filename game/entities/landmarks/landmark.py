import pygame

from isec.environment import Entity, Sprite


class Landmark(Entity):
    def __init__(self,
                 position: pygame.math.Vector2,
                 sprite: Sprite):

        super().__init__(position, sprite)
        self.rect = sprite.rect.move(position)
