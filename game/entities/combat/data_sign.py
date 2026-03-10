import typing

from isec.app import Resource
from isec.environment import Entity, Sprite


class DataSign(Entity):
    def __init__(self, side: typing.Literal["left", "right"]):
        super().__init__((100, 0), Sprite(Resource.image[f"data_sign_{side}"], position_anchor="top"))
