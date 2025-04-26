import pygame
from pygame import Vector2

from typing import Self

class RectCollider:
    """
    A rectangular collider.
    """
    x: float
    y: float
    width: float
    height: float

    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def intersecting(self, other: Self) -> bool:
        """
        Returns whether this collider intersects with another `RectCollider`.
        """
        return not (
            self.x > other.x + other.width or self.x + self.width < other.x or
            self.y > other.y + other.height or self.y + self.height < other.y
        )
    
    def collide(self, other: Self) -> Vector2:
        """
        Returns a vector that moves this collider out of another `RectCollider`. If the colliders do
        not overlap, returns a zero vector instead.
        """
        if not self.intersecting(other):
            return Vector2(0, 0)
        
        # center x and y
        self_cx = self.x + self.width / 2
        self_cy = self.y + self.height / 2
        other_cx = other.x + other.width / 2
        other_cy = other.y + other.height / 2

        # find which direction to move
        dx = other_cx - self_cx
        dy = other_cy - self_cy

        x_range = self.width / 2 + other.width / 2
        y_range = self.height / 2 + other.height / 2

        mx = x_range - abs(dx)
        my = y_range - abs(dy)

        if mx <= my:
            if dx < 0:
                return Vector2(mx, 0)
            else:
                return Vector2(-mx, 0)
        else:
            if dy < 0:
                return Vector2(0, my)
            else:
                return Vector2(0, -my)
    
    def pg_rect(self) -> pygame.Rect:
        """
        Returns a `pygame.Rect` object representing the collider's area.
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)