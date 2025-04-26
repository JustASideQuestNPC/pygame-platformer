import pygame

from src.engine.input import Input, GpAxis
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
    MAX_FALL_SPEED = 900 # pixels per second
    # this is a "soft cap" - the player can't normally move faster than this, but they can keep any
    # speed above it that they get from other sources
    MAX_RUN_SPEED = 300 # pixels per second
    JUMP_IMPULSE = -400 # pixels per second
    MAX_JUMPS = 2

    # engine properties
    tags = [EntityTag.PLAYER]

    # instance properties
    position: pygame.Vector2
    velocity: pygame.Vector2
    collider: RectCollider
    jumps_remaining: int

    def __init__(self, x: float, y: float):
        super().__init__()
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.collider = RectCollider(
            x - Player.SIZE[0] / 2, y - Player.SIZE[1] / 2,
            Player.SIZE[0], Player.SIZE[1]
        )
        self.jumps_remaining = 0

    def update(self, dt):
        # get movement input
        move_dir = 0
        # joysticks take priority
        if Input.last_input_source() == 'gamepad':
            stick_pos = Input.get_gamepad().axis_value(GpAxis.LEFT_STICK_X)
            if stick_pos < -0.5:
                move_dir = -1
            elif stick_pos > 0.5:
                move_dir = 1
        
        if move_dir == 0:
            if Input.active('left'):  move_dir -= 1
            if Input.active('right'): move_dir += 1

        self.velocity.x = Player.MAX_RUN_SPEED * move_dir

        # jump or apply gravity
        if self.jumps_remaining > 0 and Input.active('jump'):
            self.jumps_remaining -= 1
            # jumping is an impulse, so delta time doesn't affect it
            self.velocity.y = Player.JUMP_IMPULSE
        else:
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
                    if trans_vec.y < 0:
                        self.jumps_remaining = Player.MAX_JUMPS

    def render(self, rt):
        pygame.draw.rect(rt, Player.COLOR, self.collider.pg_rect())