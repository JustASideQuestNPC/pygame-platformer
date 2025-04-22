from configparser import ConfigParser

import pygame

import src.engine.input as input

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

# misc. variables
dt: float = 0
""" The time between the last two frames, in seconds. """

# main game loop
running = True
while running:
    dt = clock.tick(60) / 1000 # native delta time is in milliseconds

    for event in pygame.event.get():
        # x button or alt+f4 pressed
        if event.type == pygame.QUIT:
            running = False

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

    # blit to the screen
    pygame.display.flip()

pygame.quit()