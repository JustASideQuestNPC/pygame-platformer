from configparser import ConfigParser

import pygame

from src.engine.input import Input
from src.engine.gamepad import Gamepad

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
Input.add_action(
    name='hold',
    keys=['a', 'spacebar', 'left mouse'],
    buttons=['a', 'left trigger']
)
Input.add_action(
    name='hold chord',
    keys=['b', 'right mouse'],
    buttons=['b', 'left trigger full pull'],
    chord=True
)
Input.add_action(
    name='press',
    keys=['c', 'left click'],
    buttons=['x', 'left stick click'],
    mode='press'
)
Input.add_action(
    name='press chord',
    keys=['shift', 'middle mouse'],
    buttons=['y', 'right bumper'],
    mode='press',
    chord=True
)

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

    Input.update(dt)

    # clear the canvas
    screen.fill("#ffffff")

    c = '#00ff00' if Input.active('hold') else '#ff0000'
    pygame.draw.circle(screen, c, (100, 100), 75)

    c = '#00ff00' if Input.active('hold chord') else '#ff0000'
    pygame.draw.circle(screen, c, (300, 100), 75)

    c = '#00ff00' if Input.active('press') else '#ff0000'
    pygame.draw.circle(screen, c, (100, 300), 75)

    c = '#00ff00' if Input.active('press chord') else '#ff0000'
    pygame.draw.circle(screen, c, (300, 300), 75)

    text_lines: list[str] = [
        f'Last input source: {Input.last_input_source()}'
    ]

    for [i, line] in enumerate(text_lines):
        screen.blit(debug_font.render(line, 1, "#000000", "#ffffff"), (420, i * 30 + 10))

    # display onscreen
    pygame.display.flip()

pygame.quit()