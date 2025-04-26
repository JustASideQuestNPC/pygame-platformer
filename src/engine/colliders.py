import pygame

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

    def colliding(self, other: Self, trans_vec: pygame.Vector2=None) -> bool:
        """
        Returns whether this collider intersects with another `RectCollider`.

        Args:
            trans_vec (pygame.Vector2, optional):
                Reference to a translation vector. If the colliders intersect, this vector will be
                set to the smallest vector that moves this collider out of the other one. Otherwise,
                it will be set to zero.
        """
        intersecting = not (
            self.x > other.x + other.width or self.x + self.width < other.x or
            self.y > other.y + other.height or self.y + self.height < other.y
        )

        # skip everything else if we're not getting a translation vector
        if trans_vec == None:
            return intersecting
        
        if not intersecting:
            trans_vec.update(0, 0)
            return False
        
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
                trans_vec.update(mx, 0)
            else:
                trans_vec.update(-mx, 0)
        else:
            if dy < 0:
                trans_vec.update(0, my)
            else:
                trans_vec.update(0, -my)
        return True
    
    def pg_rect(self) -> pygame.Rect:
        """
        Returns a `pygame.Rect` object representing the collider's area.
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)