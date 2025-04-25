from configparser import ConfigParser

import pygame

from src.engine.input import Input
from src.engine.gamepad import Gamepad
from src.engine.engine import Engine
from src.entities.test_entities import TestEntity, TestEntityFast

# get configs
config = ConfigParser()
config.read('_config.ini')

# pygame and engine setup
pygame.init()
screen = pygame.display.set_mode((
    int(config['Graphics']['screen_width']), int(config['Graphics']['screen_height'])
))
clock = pygame.time.Clock()
Engine.init(clock, screen)

# input setup
Input.add_action(
    name='slow time',
    keys=['left mouse', 'space']
)

Engine.add_entity(TestEntity(screen.get_width() / 2, screen.get_height() / 2))
Engine.add_entity(TestEntityFast(screen.get_width() / 2, screen.get_height() / 2))

# misc. variables
dt: float = 0
""" The time between the last two frames in seconds. """

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
    Engine.update()

    if Input.active('slow time'):
        Engine.time_scale = 0.5
    else:
        Engine.time_scale = 1

    # clear the canvas
    screen.fill("#ffffff")
    Engine.render()

    # display onscreen
    pygame.display.flip()

pygame.quit()