import pygame

from src.engine.engine import EntityBase
from src.engine.colliders import RectCollider
from src.CONSTANTS import EntityTag

class Wall(EntityBase):
    """
    A basic wall.
    """
    # static configs
    COLOR = 0x282c34 # dark gray

    # engine properties
    display_layer = -5
    tags = [EntityTag.WALL, EntityTag.HAS_WALL_COLLISION]

    # instance properties
    collider: RectCollider

    def __init__(self, x: float, y: float, width: float, height: float):
        super().__init__()
        self.collider = RectCollider(x, y, width, height)

    def render(self, rt):
        pygame.draw.rect(rt, Wall.COLOR, self.collider.pg_rect())