import pygame
from pygame.math import Vector2

from src.engine.engine import EntityBase, EngineTag

class TestEntity(EntityBase):
    display_layer = 5

    SPEED = 300
    MOVE_DISTANCE = 200

    start_x: float
    position: Vector2
    direction: int = 1

    def __init__(self, x: float, y: float):
        super().__init__()
        self.start_x = x
        self.position = Vector2(x, y)

    def render(self, rt):
        pygame.draw.circle(rt, (255, 0, 0), self.position, 20)

    def update(self, dt):
        self.position.x += TestEntity.SPEED * dt * self.direction
        if (self.position.x < self.start_x - TestEntity.MOVE_DISTANCE
            or self.position.x > self.start_x + TestEntity.MOVE_DISTANCE):

            self.direction *= -1

class TestEntityFast(EntityBase):
    tags = [EngineTag.USES_RAW_DELTA_TIME]

    SPEED = 300
    MOVE_DISTANCE = 200

    start_y: float
    position: Vector2
    direction: int = 1

    def __init__(self, x: float, y: float):
        super().__init__()
        self.start_y = y
        self.position = Vector2(x, y)

    def render(self, rt):
        pygame.draw.circle(rt, (0, 0, 255), self.position, 20)

    def update(self, dt):
        self.position.y += TestEntity.SPEED * dt * self.direction
        if (self.position.y < self.start_y - TestEntity.MOVE_DISTANCE
            or self.position.y > self.start_y + TestEntity.MOVE_DISTANCE):

            self.direction *= -1