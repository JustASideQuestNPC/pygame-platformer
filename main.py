import pygame
from configobj import ConfigObj

from src.engine.input import Input
from src.engine.gamepad import Gamepad
from src.engine.engine import Engine
from src.entities.entities import Wall, Player

config = ConfigObj('_config.ini')

# pygame and engine setup
pygame.init()
screen = pygame.display.set_mode((
    int(config['Graphics']['screen_width']), int(config['Graphics']['screen_height'])
))
clock = pygame.time.Clock()
Engine.init(clock, screen)

# input setup
keybinds = config['Input']['Keybinds']
press_actions = config['Input']['press-actions']
for name, bind in keybinds.items():
    Input.add_action(
        name=name,
        keys=bind['keys'],
        buttons=bind['buttons'],
        mode='press' if name in press_actions else 'hold'
    )

# misc. variables
dt: float = 0
""" The time between the last two frames in seconds. """

Engine.add_entity(Wall(240, 620, 800, 50))
Engine.add_entity(Player(screen.get_width() / 2, 520))

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

    # clear the canvas
    screen.fill("#ffffff")
    Engine.render()

    # display onscreen
    pygame.display.flip()

pygame.quit()