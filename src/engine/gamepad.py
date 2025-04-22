from typing import Self
from enum import IntEnum

import pygame

class GpAxis(IntEnum):
    """ An axis on the gamepad. """
    LEFT_STICK_X = 0
    LEFT_STICK_Y = 1
    RIGHT_STICK_X = 2
    RIGHT_STICK_Y = 3
    LEFT_TRIGGER = 4
    """ L2 on Playstation controllers. """
    RIGHT_TRIGGER = 5
    """ R2 on Playstation controllers. """
    DPAD_X = 6
    DPAD_Y = 7

class GpButton(IntEnum):
    """ A button on the gamepad. """
    A = 0
    """ X on Playstation controllers. """
    B = 1
    """ Circle on Playstation controllers. """
    X = 2
    """ Square on Playstation controllers. """
    Y = 3
    """ Triangle on Playstation controllers. """
    LEFT_BUMPER = 4
    """ L1 on Playstation controllers. """
    RIGHT_BUMPER = 5
    """ R1 on Playstation controllers. """
    BACK = 6
    """ Share on Playstation controllers. """
    START = 7
    """ Options on Playstation controllers. """
    LEFT_STICK_CLICK = 8
    """ L3 on Playstation controllers. """
    RIGHT_STICK_CLICK = 9
    """ R3 on Playstation controllers. """
    GUIDE = 10
    """ PS Logo on Playstation controllers. """
    LEFT_TRIGGER = 11
    """
    L2 on Playstation controllers. This is a "soft pull" and activates if the trigger is at least
    30% pulled.
    """
    RIGHT_TRIGGER = 12
    """
    R2 on Playstation controllers. This is a "soft pull" and activates if the trigger is at least
    30% pulled.
    """
    LEFT_TRIGGER_FULL_PULL = 13
    """
    L2 on Playstation controllers. This is a "full pull" and activates if the trigger is at least
    95% pulled.
    """
    RIGHT_TRIGGER_FULL_PULL = 14
    """
    R2 on Playstation controllers. This is a "full pull" and activates if the trigger is at least
    95% pulled.
    """

class GpThumbstick(IntEnum):
    """ A thumbstick on the gamepad. """
    LEFT = 0
    RIGHT = 1
    DPAD = 2

def _apply_deadzone(value: float, inner: float, outer: float) -> float:
    """
    Applies deadzone to an analog input. Both the input and output are between 0 and 1.

    Parameters:
        inner (float):
            Input values closer to 0 than this will be snapped to 0. Must be >= 0.
        outer (float):
            Input values closer to -1 or 1 than this will be snapped to -1 or 1 respectively. Must
            be >= 0.
    """
    outer = 1 - outer # makes the math easier

    magnitude = abs(value)
    sign = 1 if value >= 0 else -1

    if magnitude < inner:
        return 0.0
    elif magnitude > outer:
        return sign * 1.0
    else:
        scaled = (magnitude - inner) / (outer - inner)
        return sign * scaled

class Gamepad:
    """
    A gamepad. Guaranteed support for Xbox 360 controllers. Probable support for other Xbox
    controllers. No support for Playstation or Nintendo controllers.
    """

    # static variables
    _active_joystick_ids: list[int] = []
    """
    **[Static]**The ids of every joystick that is currently being used by a Gamepad instance. Used
    to prevent multiple instances from trying to use the same joystick.
    """
    _instance_list: list[Self] = []
    """
    **[Static]**References to active gamepads; used to update all instances at once.
    """

    deadzone_inner: float = 0.1
    """
    **[Static]** Inner joystick deadzone. Joystick axis values closer to 0 than this will be snapped
    to 0. No effect on triggers.
    """
    deadzone_outer: float = 0.05
    """
    **[Static]** Outer joystick deadzone. Joystick axis values closer to -1 or 1 than this will be
    snapped to -1 or 1 respectively. No effect on triggers.
    """

    # instance variables
    _pg_joystick: pygame.joystick.JoystickType
    """ The actual pygame joystick. """

    # static methods
    @staticmethod
    def update_connected(event: pygame.event.Event):
        """
        Updates all `Gamepad` instances when a `JOYDEVICEADDED` or `JOYDEVICEREMOVED` event occurs.
        Does nothing (and is safe to call) if the event is not one of those events.
        """
        if event.type == pygame.JOYDEVICEADDED or event.type == pygame.JOYDEVICEREMOVED:
            for instance in Gamepad._instance_list:
                # only one instance will ever handle the event at once
                if instance._handle_event(event):
                    break

    # instance methods
    def __init__(self):
        self._pg_joystick = None # start disconnected
        Gamepad._instance_list.append(self)

    def _handle_event(self, event: pygame.event.Event) -> bool:
        if self._pg_joystick == None and event.type == pygame.JOYDEVICEADDED:
            # only connect to xbox controllers (because they're the only supported ones) and make
            # sure the joystick hasn't already been taken - this *probably* won't ever happen, but
            # better safe than sorry
            joystick = pygame.joystick.Joystick(event.device_index)
            name = joystick.get_name().lower()
            if event.device_index not in Gamepad._active_joystick_ids and 'xbox' in name:
                self._pg_joystick = joystick
                Gamepad._active_joystick_ids.append(event.device_index)
                print(f'Connected to joystick "{joystick.get_name()}" (id {event.device_index})')
                return True
        elif self._pg_joystick != None and event.type == pygame.JOYDEVICEREMOVED:
            if event.instance_id == self._pg_joystick.get_instance_id():
                self._pg_joystick = None
                Gamepad._active_joystick_ids.remove(event.instance_id)
                print(f'Disconnected from joystick {event.instance_id}')
                return True

        return False

    def connected(self) -> bool:
        """ Returns whether the gamepad is connected. """
        return self._pg_joystick != None
    
    def button_down(self, button: GpButton) -> bool:
        """
        Returns whether a button is currently pressed. If the gamepad is disconnected, this method
        always returns False.
        """

        if self._pg_joystick == None:
            return False
        
        # triggers are handled seperately because they're fun and quirky and not actually buttons
        if button == GpButton.LEFT_TRIGGER:
            return self.axis_value(GpAxis.LEFT_TRIGGER) >= 0.25
        elif button == GpButton.LEFT_TRIGGER_FULL_PULL:
            return self.axis_value(GpAxis.LEFT_TRIGGER) >= 0.95
        elif button == GpButton.RIGHT_TRIGGER:
            return self.axis_value(GpAxis.RIGHT_TRIGGER) >= 0.25
        elif button == GpButton.RIGHT_TRIGGER_FULL_PULL:
            return self.axis_value(GpAxis.RIGHT_TRIGGER) >= 0.95
        else:
            return self._pg_joystick.get_button(button)
    
    def axis_value(self, axis: GpAxis, raw_value: bool=False) -> float:
        """
        Returns the value of an analog axis. Joystick axes are between -1 and 1, where -1 is all the
        way left/up and 1 is all the way right/down. Trigger axes are between 0 and 1, where 1 is a
        full pull. Dpad axes are -1, 1, or 0, where -1 is left/up and 1 is right/down. If the
        gamepad is disconnected, this method always returns 0.

        Args:
            raw_value (bool, default=False):
                If True, deadzone is not applied to analog axes. Triggers and the dpad never have
                deadzone applied.
        """

        if self._pg_joystick == None:
            return 0
        
        if axis == GpAxis.DPAD_X:
            return self._pg_joystick.get_hat(0)[0]
        elif axis == GpAxis.DPAD_Y:
            # for some reason, ONLY the dpad y axis is flipped
            return self._pg_joystick.get_hat(0)[1] * -1
        
        if axis == GpAxis.LEFT_TRIGGER or axis == GpAxis.RIGHT_TRIGGER:
            return self._pg_joystick.get_axis(axis) / 2 + 0.5 # all axes are -1 to 1 internally
        else:
            if raw_value:
                return self._pg_joystick.get_axis(axis)
            else:
                return _apply_deadzone(self._pg_joystick.get_axis(axis), self.deadzone_inner,
                                       self.deadzone_outer)

    def stick_pos(self, stick: GpThumbstick, raw_value: bool=False) -> pygame.Vector2:
        """
        Returns a `Vector2` with the position of a thumbstick or the dpad. The x and y components
        are between -1 and 1, where -1 is all the way left/up and 1 is all the way right/down. If
        the gamepad is disconnected, this method always returns a zero vector.

        Args:
            raw_value (bool, default=False):
                If True, deadzone is not applied. No effect on the dpad
        """

        if stick == GpThumbstick.LEFT:
            return pygame.Vector2(
                self.axis_value(GpAxis.LEFT_STICK_X, raw_value),
                self.axis_value(GpAxis.LEFT_STICK_Y, raw_value)
            )
        elif stick == GpThumbstick.RIGHT:
            return pygame.Vector2(
                self.axis_value(GpAxis.RIGHT_STICK_X, raw_value),
                self.axis_value(GpAxis.RIGHT_STICK_Y, raw_value)
            )
        else: # stick == GpThumbstick.DPAD
            return pygame.Vector2(
                self.axis_value(GpAxis.DPAD_X, raw_value),
                self.axis_value(GpAxis.DPAD_Y, raw_value)
            )
    
    def stick_vector(self, stick: GpThumbstick) -> pygame.Vector2:
        """
        Returns a normalized `Vector2` with the position of a thumbstick or the dpad. The x and y
        components are between -1 and 1, where -1 is all the way left/up and 1 is all the way
        right/down. If the gamepad is disconnected, this method always returns a zero vector.
        """

        v: pygame.Vector2 = None
        if stick == GpThumbstick.LEFT:
            v = pygame.Vector2(
                self.axis_value(GpAxis.LEFT_STICK_X),
                self.axis_value(GpAxis.LEFT_STICK_Y)
            )
        elif stick == GpThumbstick.RIGHT:
            v = pygame.Vector2(
                self.axis_value(GpAxis.RIGHT_STICK_X),
                self.axis_value(GpAxis.RIGHT_STICK_Y)
            )
        else: # stick == GpThumbstick.DPAD
            v = pygame.Vector2(
                self.axis_value(GpAxis.DPAD_X),
                self.axis_value(GpAxis.DPAD_Y)
            )
        
        if v.x != 0 or v.y != 0:
            return v.normalize()
        return v