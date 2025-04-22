from configparser import ConfigParser

import pygame

import src.engine.input as input
from src.engine.gamepad import Gamepad, GpAxis, GpButton, GpThumbstick

# get configs
config = ConfigParser()
config.read('_config.ini')

# pygame setup
pygame.init()
screen = pygame.display.set_mode((
    int(config['Graphics']['screen_width']), int(config['Graphics']['screen_height'])
))
clock = pygame.time.Clock()

# set up input
input.add_action(
    name='hold',
    keys=['a', 'spacebar', 'left mouse'],
)
input.add_action(
    name='hold chord',
    keys=['b', 'enter', 'right mouse'],
    chord=True
)
input.add_action(
    name='press',
    keys=['c', 'left click'],
    mode='press'
)
input.add_action(
    name='press chord',
    keys=['shift', 'middle mouse'],
    mode='press',
    chord=True
)
gamepad = Gamepad()

# misc. variables
dt: float = 0
""" The time between the last two frames, in seconds. """
debug_font = pygame.font.SysFont('monospace', 24)

# main game loop
running = True
while running:
    dt = clock.tick(60) / 1000 # native delta time is in milliseconds

    for event in pygame.event.get():
        # x button or alt+f4 pressed
        if event.type == pygame.QUIT:
            running = False
        # this does nothing if the event isn't a joystick event
        Gamepad.update_connected(event)

    input.update(dt)

    # clear the canvas
    screen.fill("#ffffff")

    c = '#00ff00' if input.active('hold') else '#ff0000'
    pygame.draw.circle(screen, c, (100, 100), 75)

    c = '#00ff00' if input.active('hold chord') else '#ff0000'
    pygame.draw.circle(screen, c, (300, 100), 75)

    c = '#00ff00' if input.active('press') else '#ff0000'
    pygame.draw.circle(screen, c, (100, 300), 75)

    c = '#00ff00' if input.active('press chord') else '#ff0000'
    pygame.draw.circle(screen, c, (300, 300), 75)

    left_stick = gamepad.stick_pos(GpThumbstick.LEFT)
    left_stick_raw = gamepad.stick_pos(GpThumbstick.LEFT, True)
    left_stick_norm = gamepad.stick_vector(GpThumbstick.LEFT)

    right_stick = gamepad.stick_pos(GpThumbstick.RIGHT)
    right_stick_raw = gamepad.stick_pos(GpThumbstick.RIGHT, True)
    right_stick_norm = gamepad.stick_vector(GpThumbstick.RIGHT)

    dpad = gamepad.stick_pos(GpThumbstick.DPAD)
    dpad_norm = gamepad.stick_vector(GpThumbstick.DPAD)

    left_trigger = gamepad.axis_value(GpAxis.LEFT_TRIGGER)

    right_trigger = gamepad.axis_value(GpAxis.RIGHT_TRIGGER)

    text_lines: list[str] = [
        f'Gamepad: {"connected" if gamepad.connected() else "disconnected"}',
        f'Left stick: {left_stick}',
        f'Left stick (raw): {left_stick_raw}',
        f'Left stick (normalized): {left_stick_norm}',
        f'Right stick: {right_stick}',
        f'Right stick (raw): {right_stick_raw}',
        f'Right stick (normalized): {right_stick_norm}',
        f'Dpad: {dpad}',
        f'Dpad (normalized): {dpad_norm}',
        f'Left trigger: {left_trigger:.3f}',
        f'Right trigger: {right_trigger:.3f}',
    ]

    for [i, line] in enumerate(text_lines):
        screen.blit(debug_font.render(line, 1, "#000000", "#ffffff"), (420, i * 30 + 10))

    # display onscreen
    pygame.display.flip()

pygame.quit()