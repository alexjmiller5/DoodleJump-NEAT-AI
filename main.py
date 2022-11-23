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

WIDTH = 490 # Screen width constant
HEIGHT = int(WIDTH*1.5) # Screen height constant

# initialize the framerate object and clock so that we can standardize framerate
clock = pg.time.Clock()
FRAME_RATE = 60
DT = (1200/FRAME_RATE)

# Set up the drawing window
screen = pg.display.set_mode([WIDTH, HEIGHT])
pg.display.set_caption("Doodle Jump!")

# where to print the lines in the grid onscreen
vertical_lines = [i for i in range(WIDTH) if i % 20 == 0]
horizontal_lines = [i for i in range(HEIGHT) if i % 20 == 0]

# initialize objects
player = dl.Doodler(WIDTH, HEIGHT)
platforms = []
platforms.append(plat.Platform((WIDTH*0.12,HEIGHT*0.8)))

# set gravity strength
gravity = 0.0000033

score = 0

# Run until the user asks to quit
running = True
while running:

    # dt = change in time; this will standardize speeds based on framerate
    clock.tick(FRAME_RATE)

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

    for platform in platforms:
        # if the player collides with a platform, it should bounce upwards
        if platform.collided_width(player):
            print("The player collided with a platform")
            player.vel = (player.vel[0], -.031*DT)
            player.acc = (player.acc[0], 0)
            player.pos = player.prev_pos

    # make the player be affected by gravity
    # player.acc = (player.acc[0], player.acc[1] + gravity*DT)

    player.move(DT)

    # display all objects
    for platform in platforms:
        platform.display(screen)
    player.display(screen)

    pg.display.flip() # update the screen

pg.quit() # Quit pygame at the end of the game