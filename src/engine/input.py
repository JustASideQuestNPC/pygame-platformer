""" An action-based system for managing input. """

from typing import TypedDict, Literal

import pygame

class ActionData(TypedDict):
    name: str
    keys: list[str]
    mode: Literal['press', 'hold']
    chord: bool

_actions: dict[str, '_Action'] = {}
_KEY_ALIASES = {
    'up arrow': 'up',
    'down arrow': 'down',
    'left arrow': 'left',
    'right arrow': 'right',
    'shift': 'left shift',
    'ctrl': 'left ctrl',
    'alt': 'left alt',
    'caps': 'caps lock',
    'enter': 'return'
}

class _Action:
    """ Represents a single input action with any number of keyboard keys bound to it. """

    __key_codes: list[int]

    key_strings: list[str]
    name: str
    mode: Literal['press', 'hold']
    chord: bool
    active: bool = False

    def __init__(self, name: str, keys: list[str], mode: Literal['press', 'hold'], chord: bool):
        self.name = name
        self.key_strings = keys
        self.mode = mode
        self.chord = chord

        # set key codes - this requires extra logic because of key aliases
        self.__key_codes = []
        for key_name in keys:
            key_name = key_name.lower()
            if key_name in _KEY_ALIASES:
                key_name = _KEY_ALIASES[key_name]

            try:
                self.__key_codes.append(pygame.key.key_code(key_name))
            except ValueError as e:
                # re-throw with a better error message
                if e.args[0] == 'unknown key name':
                    raise ValueError(f'Invalid key "{key_name}" bound to action "{name}".')
                
    def update(self, key_states: pygame.key.ScancodeWrapper):
        """ Updates whether the action is active. """

        keys_pressed: bool = None
        if self.chord:
            self.active = all(key_states[k] for k in self.__key_codes)
        else:
            self.active = any(key_states[k] for k in self.__key_codes)

        if self.mode == 'hold':
            self.active = keys_pressed

def add_action(*, name: str, keys: list[str] = None, mode: Literal['press', 'hold'] = 'hold',
               chord: bool = False):
    """"
    Adds an action to the manager.

    Args:
        name (str):
            The name of the action (case-sensitive). If an action with the same name already exists,
            a `ValueError` is thrown.
        keys (list[str]):
            All keyboard keys or mouse buttons bound to the action.
        mode ('press' or 'hold', optional):
            Determines when the action is active. A hold action is activewhenever its keys are
            pressed. A press action is active for one frame whenever its keys are pressed, then
            deactivates until they are released and re-pressed. Defaults to 'hold'.
        chord (bool, optional):
            If true, the action only activates when all of its keys are pressed simultaneously.
            Otherwise, the action activates whenever at least one of its keys are pressed. Defaults
            to False.
    """

    # required because of early binding
    if keys == None:
        keys = []

    if name in _actions:
        raise ValueError(f'The action "{name}" already exists.')
    
    _actions[name] = _Action(name, keys, mode, chord)

def update():
    """
    Updates all actions. Should be called once per frame, every frame.
    """
    for action in _actions.items():
        action.update()

def action_data(name: str) -> ActionData:
    """
    Returns a read-only dict with the name, keys, mode, and chord setting of an action. This does
    *not* return whether an action is active; use `is_active` for that instead.

    Args:
        name (str):
            The name of the action (case-sensitive). If an action with the same name already exists,
            a `KeyError` is thrown.
    """
    if name in _actions:
        action = _actions[name]
        return {
            'name': action.name,
            'keys': action.key_strings[::],
            'mode': action.mode,
            'chord': action.chord
        }
    
    raise KeyError(f'The action "{name}" does not exist. Action names are case-sensitive.')

def is_active(name: str) -> bool:
    """
    Returns whether an action is currently active.

    Args:
        name (str):
            The name of the action (case-sensitive). If an action with the same name already exists,
            a `KeyError` is thrown.
    """
    if name in _actions:
        action = _actions[name]
        return action.active
    
    raise KeyError(f'The action "{name}" does not exist. Action names are case-sensitive.')