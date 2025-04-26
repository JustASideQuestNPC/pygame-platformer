from enum import Enum

class EntityTag(Enum):
    """ All entity-specific tags. """
    # class identifiers
    WALL = 'WALL'
    PLAYER = 'PLAYER'

    # attributes
    HAS_WALL_COLLISION = 'HAS_WALL_COLLISION'

# physics configs
GRAVITY = 600 # pixels per second squared