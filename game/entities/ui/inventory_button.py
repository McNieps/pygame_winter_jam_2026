from isec.app import Resource
from isec.environment import Entity, Sprite


class InventoryButton(Entity):
    def __init__(self):
        super().__init__((394, 294), Sprite(Resource.image["inventory_icon"], position_anchor="bottomright"))
        self.rect = self.sprite.surface.get_rect()
        self.rect.bottomright = self.position
