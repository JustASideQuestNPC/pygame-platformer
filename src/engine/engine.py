from enum import Enum
from typing import Callable

import pygame

class EngineTag(Enum):
    USES_RAW_DELTA_TIME = 0
    """
    Entities with the `USES_RAW_DELTA_TIME` tag ignore `Engine.time_scale` and always receive the
    "true" delta time in their `update()` methods.
    """

# i'd make this an abstract class, but the point of it is that all of its methods are defaults
class EntityBase:
    """ Abstract class that all game entities must extend. """
    display_layer: float = 0
    """
    When rendered, entities with a higher display layer appear on top of those with a lower display
    layer. Display layers can be any number, including non-integers and negative numbers.
    """
    tags: list[any] = []
    """
    All the entity's tags (if any). Tags are used to mark what an entity is and/or what attributes
    it has.
    """
    markForRemove: bool = False
    """ If True, the entity will be removed from the engine at the end of the next update. """
    
    def update(self, dt: float):
        """
        Called once per frame in `Engine.update()`.

        Args:
            dt (float):
                The time between the previous two frames in seconds.
        """
        pass

    def render(self, rt: pygame.Surface):
        """
        Called once per frame in `Engine.render()`.

        Args:
            rt (pygame.Surface):
                The render target that the entity should be drawn onto.
        """
        pass

    def on_add(self, ):
        """" Called once when the entity is added to the engine. """
        pass

    def on_remove(self, ):
        """ Called once when the entity is removed from the engine. """
        pass

class Engine:
    _initialized: bool = False
    _entities: list[EntityBase] = []
    """ Single list of all entities; used for everything except rendering. """
    _display_layers: dict[float, list[EntityBase]] = {}
    """ Entities grouped into display layers; used for rendering. """
    _layer_indexes: list[float] = []
    """ All active display layers. """
    _render_target: pygame.Surface = None
    """ The surface all entities should be rendered onto. """
    _clock: pygame.time.Clock = None
    """ "Speed of time" """
    _delta_time_raw: float = 0
    """ The time between the last two frames in seconds. """

    time_scale: float = 1
    """ "Speed of time". Values < 1 slow down time and values > 1 speed it up. Must be > 0. """

    @staticmethod
    def delta_time() -> float:
        """
        Returns the time between the last two frames in seconds, with the current time scale
        applied.
        """
        return Engine._delta_time_raw * Engine._time_scale
    
    @staticmethod
    def delta_time_raw() -> float:
        """
        Returns the time between the last two frames in seconds, without the current time scale
        applied.
        """
        return Engine._delta_time_raw

    @staticmethod
    def init(clock: pygame.time.Clock, render_target: pygame.Surface):
        """
        Initializes the entity with a clock for timing and a surface to render entities onto. This
        must be called exactly once before any other engine functions are used.
        """
        if Engine._initialized:
            raise RuntimeError('Engine is already initialized.')
        
        Engine._clock = clock
        Engine._render_target = render_target
        Engine._initialized = True

    @staticmethod
    def add_entity(entity: EntityBase, allow_setup: bool=True) -> EntityBase:
        """
        Adds an entity to the engine.

        Args:
            entity (EntityBase):
                An instance of any class that extends `EntityBase`.
            allow_setup (boolean, default=True):
                Whether the entity's `on_add()` method should be called.

        Returns:
            EntityBase: A reference to `entity` (this is more useful than it sounds).
        """
        if not Engine._initialized:
            raise RuntimeError('Engine must be initialized before other functions are called.')
        
        # all entities are added to the main list
        Engine._entities.append(entity)

        # add the entity to an existing layer or create a new one
        if entity.display_layer in Engine._layer_indexes:
            Engine._display_layers[entity.display_layer].append(entity)
        else:
            Engine._display_layers[entity.display_layer] = [entity]
            Engine._layer_indexes.append(entity.display_layer)
            Engine._layer_indexes.sort() # make sure everything actually stays in order

        if allow_setup:
            entity.on_add()

        return entity

    @staticmethod
    def update():
        """
        Updates all entities. This should be called once per frame along with `Engine.render()`
        """
        if not Engine._initialized:
            raise RuntimeError('Engine must be initialized before other functions are called.')
        
        # native delta time is in milliseconds
        Engine._delta_time_raw = Engine._clock.get_time() / 1000

        for entity in Engine._entities:
            # skip entities that have already been deleted
            if not entity.markForRemove:
                if EngineTag.USES_RAW_DELTA_TIME in entity.tags:
                    entity.update(Engine._delta_time_raw)
                else:
                    entity.update(Engine._delta_time_raw * Engine.time_scale)
            
        # garbage collect
        Engine.remove_if(lambda e: e.markForRemove)

    @staticmethod
    def render():
        """
        Renders all entities. This should be called once per frame along with `Engine.update()`
        """
        if not Engine._initialized:
            raise RuntimeError('Engine must be initialized before other functions are called.')
        
        for i in Engine._layer_indexes:
            layer = Engine._display_layers[i]
            for entity in layer:
                entity.render(Engine._render_target)

    @staticmethod
    def remove_if(predicate: Callable[[EntityBase], bool], silent: bool=False):
        """
        Removes all entities that a predicate function returns True for.

        Args:
            silent (bool, default=False):
                If True, entities' `on_remove()` methods are not called.
        """
        if not Engine._initialized:
            raise RuntimeError('Engine must be initialized before other functions are called.')

        # loop manually so removal methods get called
        buffer: list[EntityBase] = []
        for entity in Engine._entities:
            if predicate(entity):
                entity.on_remove()
            else:
                buffer.append(entity)
        Engine._entities = buffer

        # also filter display layers
        for i in Engine._layer_indexes:
            Engine._display_layers[i] = [e for e in Engine._display_layers[i] if not predicate(e)]

    @staticmethod
    def remove_all(silent: bool=True):
        """
        Removes all entities.

        Args:
            silent (bool, default=True):
                If True, entities' `on_remove()` methods are not called.
        """
        if not Engine._initialized:
            raise RuntimeError('Engine must be initialized before other functions are called.')
        
        # ensures removal methods get called
        Engine.remove_if(lambda e: True, silent)

        # fully reset display layers because remove_if doesn't actually remove empty ones
        Engine._display_layers = {}
        Engine._layer_indexes = []

    @staticmethod
    def remove_tagged(tag: any, silent: bool=False):
        """
        Removes all entities with a certain tag.

        Args:
            silent (bool, default=False):
                If True, entities' `on_remove()` methods are not called.
        """
        if not Engine._initialized:
            raise RuntimeError('Engine must be initialized before other functions are called.')
        
        Engine.remove_if(lambda e: tag in e.tags, silent)

    @staticmethod
    def get_all() -> list[EntityBase]:
        """ Returns a list containing references to all entities. """
        if not Engine._initialized:
            raise RuntimeError('Engine must be initialized before other functions are called.')
        
        return Engine._entities[::]
    
    @staticmethod
    def get_if(predicate: Callable[[EntityBase], bool]) -> list[EntityBase]:
        """
        Returns a list containing references to all entities that a predicate function returns True
        for.
        """
        if not Engine._initialized:
            raise RuntimeError('Engine must be initialized before other functions are called.')
        
        return [e for e in Engine._entities if predicate(e)]
    
    @staticmethod
    def get_tagged(tag: any) -> list[EntityBase]:
        """ Returns all entities with a certain tag. """
        if not Engine._initialized:
            raise RuntimeError('Engine must be initialized before other functions are called.')
        
        return Engine.get_if(lambda e: tag in e.tags)

    def __new__(cls):
        raise TypeError('Input is a static class and cannot be instantiated or subclassed.')