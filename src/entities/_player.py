import pygame

from src.engine.engine import Engine, EntityBase
from src.engine.colliders import RectCollider
from src.CONSTANTS import EntityTag, GRAVITY

class Player(EntityBase):
    """
    The player.
    """
    # static configs
    COLOR = 0x61aeee
    SIZE = (20, 32) # (width, height)
    MAX_FALL_SPEED = 600 # pixels per second

    # engine properties
    tags = [EntityTag.PLAYER]

    # instance properties
    position: pygame.Vector2
    velocity: pygame.Vector2
    collider: RectCollider

    def __init__(self, x: float, y: float):
        super().__init__()
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.collider = RectCollider(
            x - Player.SIZE[0] / 2, y - Player.SIZE[1] / 2,
            Player.SIZE[0], Player.SIZE[1]
        )

    def update(self, dt):
        # apply gravity
        self.velocity.y = min(self.velocity.y + GRAVITY * dt, Player.MAX_FALL_SPEED)

        # apply delta time and move
        self.position += self.velocity * dt
        self.collider.x = self.position.x - Player.SIZE[0] / 2
        self.collider.y = self.position.y - Player.SIZE[1] / 2

        # check for collisions
        walls = Engine.get_tagged(EntityTag.HAS_WALL_COLLISION)
        for wall in walls:
            trans_vec = pygame.Vector2() # trans rights!
            if self.collider.colliding(wall.collider, trans_vec):
                self.position += trans_vec
                self.collider.x = self.position.x - Player.SIZE[0] / 2
                self.collider.y = self.position.y - Player.SIZE[1] / 2

                # reset velocity on the correct axis
                if trans_vec.x != 0:
                    self.velocity.x = 0
                else: # a translation vector where both components are zero is impossible here
                    self.velocity.y = 0

    def render(self, rt):
        pygame.draw.rect(rt, Player.COLOR, self.collider.pg_rect())