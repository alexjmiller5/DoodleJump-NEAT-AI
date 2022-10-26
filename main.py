# Project: DoodleJump-NEAT-AI
# Authors: Alex Miller and Ruihang Liu
# Email: alexjmil@bu.edu and hrl@bu.edu
# File description (main.py): implements main
# functionality of the DoodleJump game using pygame

import pygame as pg

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
HEIGHT = WIDTH*1.5 # Screen height constant

# Set up the drawing window
screen = pg.display.set_mode([WIDTH, HEIGHT])
pg.display.set_caption("Doodle Jump!")

# initialize objects
player = Doodler()

# Run until the user asks to quit
running = True
while running:

    # Event handling
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    
    screen.fill((255, 255, 255)) # Fill the background with white
    player.display()

    pg.display.flip() # update the screen

pg.quit() # Quit pygame at the end of the game