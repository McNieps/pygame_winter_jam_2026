import typing

from isec.app import Resource
from isec.environment import Entity, Sprite


class GoButton(Entity):
    def __init__(self):
        super().__init__((0, 0), Sprite(Resource.image["go_button"]))
        self.callback: typing.Callable[[], None] = lambda:None
        self._active = False
        self.rect = self.sprite.surface.get_rect()

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, value: bool) -> None:
        self._active = value
        self.sprite.displayed = value

    def move(self, new_pos):
        self.position.xy = new_pos
        self.rect.center = new_pos
