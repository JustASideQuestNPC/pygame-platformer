from configparser import ConfigParser

import pygame

import src.engine.input as input

config = ConfigParser()
config.read('_config.ini')

# pygame setup
pygame.init()
screen = pygame.display.set_mode((
    int(config['Graphics']['screen_width']), int(config['Graphics']['screen_height'])
))
clock = pygame.time.Clock()

# main game loop
running = True
while running:
    for event in pygame.event.get():
        # x button or alt+f4 pressed
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            print(pygame.key.name(event.key))

    # clear the canvas
    screen.fill("purple")

    # blit to the screen
    pygame.display.flip()

    clock.tick(60)

pygame.quit()