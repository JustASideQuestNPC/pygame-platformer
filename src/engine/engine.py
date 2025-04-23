import pygame

# i'd make this an abstract class, but the point of it is that all of its methods are defaults
class EntityBase:
    """ Abstract class that all game entities must extend. """
    tags: list[any] = []
    """
    All the entity's tags (if any). Tags are used to mark what an entity is and/or what attributes
    it has.
    """
    markForRemove: bool = False
    """ If True, the entity will be removed from the engine at the end of the next update. """

    # hack the constructor to prevent instantiaton because this technically isn't an abstract class
    def __new__(cls):
        if cls is EntityBase:
            raise TypeError('EntityBase is an abstract class and cannot be instantiated.')
    
    def update(dt: float):
        """
        Called once per frame in `Engine.update()`.

        Args:
            dt (float):
                The time between the previous two frames in seconds.
        """
        pass

    def render(rt: pygame.Surface):
        """ Called once per frame in `Engine.render()`. """
        pass