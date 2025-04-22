""" An action-based system for managing input. """

from typing import TypedDict, Literal

import pygame

class ActionData(TypedDict):
    name: str
    keys: list[str]
    mode: Literal['press', 'hold']
    chord: bool

_KEY_ALIASES = {
    'up arrow': 'up',
    'down arrow': 'down',
    'left arrow': 'left',
    'right arrow': 'right',
    'shift': 'left shift',
    'ctrl': 'left ctrl',
    'alt': 'left alt',
    'caps': 'caps lock',
    'enter': 'return',
    'spacebar': 'space'
}

_MOUSE_BUTTONS = {
    'left mouse': 0,
    'left click': 0,
    'mouse 1': 0,
    'middle mouse': 1,
    'middle click': 1,
    'mouse 3': 1,
    'right mouse': 2,
    'right click': 2,
    'mouse 2': 2
}

_actions: dict[str, '_Action'] = {}

_buffer_duration: float = 0

class _Action:
    """ Represents a single input action with any number of keyboard keys bound to it. """

    __key_codes: list[int]
    __mouse_codes: list[int]

    key_strings: list[str]
    name: str
    mode: Literal['press', 'hold']
    chord: bool
    active: bool = False

    # only used by press-type actions
    was_active: bool = False
    buffer_remaining: float = 0

    def __init__(self, name: str, keys: list[str], mode: Literal['press', 'hold'], chord: bool):
        self.name = name
        self.key_strings = keys
        self.mode = mode
        self.chord = chord

        # set key codes - this requires some extra logic because of key aliases
        self.__key_codes = []
        self.__mouse_codes = []
        for key_name in keys:
            key_name = key_name.lower()

            # mouse buttons are passed as part of the key list but need to be tracked seperately
            if key_name in _MOUSE_BUTTONS:
                self.__mouse_codes.append(_MOUSE_BUTTONS[key_name])
            else:
                if key_name in _KEY_ALIASES:
                    key_name = _KEY_ALIASES[key_name]
                try:
                    self.__key_codes.append(pygame.key.key_code(key_name))
                except ValueError as e:
                    # re-throw with a better error message
                    if e.args[0] == 'unknown key name':
                        raise ValueError(f'Invalid key "{key_name}" bound to action "{name}".')
                
    def update(self, key_states: pygame.key.ScancodeWrapper, mouse_states: tuple[bool, bool, bool],
               dt: float):
        """ Updates whether the action is active. """

        keys_pressed: bool = None
        if self.chord:
            keys_pressed = (all(key_states[k] for k in self.__key_codes)
                            and all(mouse_states[m] for m in self.__mouse_codes))
        else:
            keys_pressed = (any(key_states[k] for k in self.__key_codes)
                            or any(mouse_states[m] for m in self.__mouse_codes))

        if self.mode == 'hold':
            self.active = keys_pressed
        else: # self.mode == 'press'
            if keys_pressed:
                if self.buffer_remaining > 0:
                    self.buffer_remaining -= dt
                    self.active = True
                elif self.was_active:
                    self.active = False
                else:
                    self.active = True
                    self.was_active = True
                    self.buffer_remaining = _buffer_duration
            else:
                self.active = False
                self.was_active = False

def get_buffer_duration() -> float:
    """ Returns how long press-type actions can be buffered for, in seconds. """
    return _buffer_duration

def set_buffer_duration(duration: float):
    """ Sets how long press-type actions can be buffered for, in seconds. """
    _buffer_duration = duration

def add_action(*, name: str, keys: list[str]=None, mode: Literal['press', 'hold']='hold',
               chord: bool=False):
    """"
    Adds an action to the manager.

    Args:
        name (str):
            The name of the action (case-sensitive). If an action with the same name already exists,
            a `ValueError` is thrown.
        keys (list[str]):
            All keyboard keys or mouse buttons bound to the action.
        mode ('press' or 'hold', default='hold'):
            Determines when the action is active. A hold action is active whenever its keys are
            pressed. A press action is active for one frame whenever its keys are pressed, then
            deactivates until they are released and re-pressed.
        chord (bool, default=False):
            If True, the action only activates when all of its keys are pressed simultaneously.
            Otherwise, the action activates when at least one of its keys are pressed.
    """

    # required because of early binding
    if keys == None:
        keys = []

    if name in _actions:
        raise ValueError(f'The action "{name}" already exists.')
    
    _actions[name] = _Action(name, keys, mode, chord)

def update(dt: float):
    """
    Updates all actions. Should be called once per frame, every frame.

    Args:
        dt (float):
            The time between the last two frames, in seconds.
    """
    key_states = pygame.key.get_pressed()
    mouse_states = pygame.mouse.get_pressed(3)
    for action in _actions.values():
        action.update(key_states, mouse_states, dt)

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
    
    raise KeyError(f'The action "{name}" does not exist (action names are case-sensitive).')

def active(name: str, reset_buffer=True) -> bool:
    """
    Returns whether an action is currently active.

    Args:
        name (str):
            The name of the action (case-sensitive). If an action with the same name already exists,
            a `KeyError` is thrown.

        reset_buffer (bool, default=True):
            If True, the action's buffer is reset if it is active. This deactivates it on the next
            update and prevents press-type actions from activating multiple times. Note: even when
            this is True, the action will remain active until the next time `input.update()` is
            called.
    """
    if name in _actions:
        action = _actions[name]
        if action.active and reset_buffer:
            # has no effect if the action is a hold
            action.buffer_remaining = 0
        return action.active
    
    raise KeyError(f'The action "{name}" does not exist (action names are case-sensitive).')

def action_names() -> list[str]:
    """ Returns a list with the names of every action. """
    return [k for k in _actions.keys()]