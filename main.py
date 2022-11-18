# Project: DoodleJump-NEAT-AI
# Authors: Alex Miller and Ruihang Liu
# Email: alexjmil@bu.edu and hrl@bu.edu
# File description (main.py): implements main
# functionality of the DoodleJump game using pygame

import pygame as pg
import doodler as dl
import plat

pg.init()

# Import pygame.locals for easier access to key coordinates
# from pygame.locals import *
from pygame.locals import (
    RLEACCEL,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

WIDTH = 400 # Screen width constant
HEIGHT = int(WIDTH*1.5) # Screen height constant

# Set up the drawing window
screen = pg.display.set_mode([WIDTH, HEIGHT])
pg.display.set_caption("Doodle Jump!")

# where to print the lines in the grid onscreen
vertical_lines = [i for i in range(WIDTH) if i % 20 == 0]
horizontal_lines = [i for i in range(HEIGHT) if i % 20 == 0]

# initialize objects
player = dl.Doodler(WIDTH, HEIGHT)
platforms = []
platforms.append(plat.Platform((WIDTH//4,int(HEIGHT*0.8))))

# set gravity strength
gravity = (0, -1)


# Run until the user asks to quit
running = True
while running:

    # Event handling
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    
    screen.fill((248, 239, 230)) # Fill the background with DoodleJump color

    # display DoodleJump grid
    for y_pos in horizontal_lines:
        pg.draw.line(screen, (233, 225, 214), (0, y_pos), (WIDTH, y_pos))
    for x_pos in vertical_lines:
        pg.draw.line(screen, (233, 225, 214), (x_pos, 0), (x_pos, HEIGHT))

    player.pos = tuple(sum(x) for x in zip(player.pos, gravity))

    for platform in platforms:
        platform.display(screen)
        if player.pos[0] > platform.pos[0] - platform.

    player.display(screen)

    pg.display.flip() # update the screen

pg.quit() # Quit pygame at the end of the game