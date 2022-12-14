# Project: DoodleJump-NEAT-AI
# Authors: Alex Miller and Ruihang Liu
# Email: alexjmil@bu.edu and hrl@bu.edu
# File description (main.py): implements main
# functionality of the DoodleJump game using pygame

import pygame as pg
from Doodler import *
from plat import *
import random

pg.init()

# Import pygame.locals for easier access to key coordinates
# from pygame.locals import *
from pygame.locals import (
    KEYDOWN,
    K_SPACE,
    K_RIGHT,
    K_LEFT,
    QUIT,
)

WIDTH = 493 # Screen width constant
HEIGHT = int(WIDTH*1.5) # Screen height constant

# initialize the framerate object and clock so that we can standardize framerate
clock = pg.time.Clock()
FRAME_RATE = 60
DT = (1200/FRAME_RATE)

# Set up the drawing window
screen = pg.display.set_mode([WIDTH, HEIGHT])
pg.display.set_caption("Doodle Jump!")

# initialize pygame fonts
pg.font.init()
my_font = pg.font.SysFont('Comic Sans MS', 30)

# where to print the lines in the grid onscreen
vertical_lines = [i for i in range(WIDTH) if i % 20 == 0]
horizontal_lines = [i for i in range(HEIGHT) if i % 20 == 0]

# NEAT variables
GENERATION_SIZE = 100

# initialize objects
platforms = []
platforms.append(Platform((WIDTH*0.12,HEIGHT*0.8)))
player = Doodler(((WIDTH*0.12, HEIGHT*0.8 - 100)))
player.pos = (player.pos[0] - 0.5*player.width + 0.5*platforms[0].width + 10, player.pos[1])
doodlers = [Doodler((WIDTH/2, 0.9*HEIGHT)) for i in range(GENERATION_SIZE)]
for doodler in doodlers:
    doodler.vel = (player.vel[0], -0.025*DT)

# boolean variables to keep track of the game state
start_game = False
playing = False

# Run until the user asks to quit
running = True

# for platform generation control
prev_score = 0

while running:

    # this will standardize speeds based on framerate
    clock.tick(FRAME_RATE)

    # Event handling
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        # if event.type == KEYDOWN:
        #     if event.key == K_SPACE:
        #         start_game = True

    # create the starting when the user starts playing
    if start_game and not playing:
        
        plat_width = platforms[0].width
        plat_height = platforms[0].height
        platforms.clear()

        # generate the 30 platforms to start off the game with
        while len(platforms) <= 30:
            new_plat_pos = (random.random()*(WIDTH - plat_width), random.random()*(HEIGHT - 2*plat_height) - plat_height - 40)
            new_plat = Platform(new_plat_pos)
            is_too_close = False
            for platform in platforms:
                if new_plat.is_too_close_to(platform):
                    is_too_close = True
            if not is_too_close:
                platforms.append(Platform(new_plat_pos))

        # set the player's starting position, velocity and acceleration
        player.pos = (WIDTH/2, 0.9*HEIGHT)
        player.vel = (player.vel[0], -0.025*DT)
        player.acc = (0, 0)
        start_game = False

    # work the functionality for the screen when the user has started the game
    if playing:

        # find the keys the are pressed down
        keys = pg.key.get_pressed()

        # allow the user to move the player via keyboard input if the keys are pressed down
        if keys[K_RIGHT]:
            player.move_right(DT)
        elif keys[K_LEFT]:
            player.move_left(DT)
        elif player.vel[0] > 0.0005*DT:
            player.acc = (-0.0001*DT, player.acc[1])
        elif player.vel[0] < -0.0005*DT:
            player.acc = (0.0001*DT, player.acc[1])
        else:
            player.vel = (0, player.vel[1])
            player.acc = (0, player.acc[1])

        # Event handling for keyboard input
        for event in pg.event.get():
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    player.vel = (-.001*DT, player.vel[1])
                    player.acc = (0, player.acc[1])
                if event.key == K_RIGHT:
                    player.vel = (.001*DT, player.vel[1])
                    player.acc = (0, player.acc[1])

        # remove offscreen platforms
        for platform in platforms:
            if platform.pos[1] > HEIGHT + platforms[0].height:
                platforms.remove(platform)

        ################################################################################################################################################################
        # platform generation as the player gets higher and higher
        ################################################################################################################################################################

        # create platforms that are always reachable by the doodler
        if int(player.score) % 13 == 0 and int(player.score) != prev_score:
            platforms.append(Platform((random.random()*(WIDTH - plat_width), -100)))
            prev_score = int(player.score)
            

        # keep track of the number of platforms that will be put on the screen
        # this number will decrease as the player's score gets higher and eventually reach 0
        extra_platform_num = int(30 - player.score**0.5)

        tries = 0
        while len(platforms) - 4 <= extra_platform_num:
            if tries > 10:
                break
            new_plat_pos = (random.random()*(WIDTH - plat_width), -1*platforms[0].height - 20)
            new_plat = Platform(new_plat_pos)
            is_too_close = False
            for platform in platforms:
                if new_plat.is_too_close_to(platform):
                    is_too_close = True
            if not is_too_close:
                platforms.append(Platform(new_plat_pos))
                tries = 0
            tries += 1

        ################################################################################################################################################################
        # scroll the game upwards as the player gets higher and higher
        ################################################################################################################################################################
        
        if player.pos[1] < 0.33*HEIGHT and player.vel[1] < 0:
            offset = player.vel[1]
            player.score -= offset
            player.pos = (player.pos[0], player.pos[1] - offset*DT)
            for platform in platforms:
                platform.pos = (platform.pos[0], platform.pos[1] - offset*DT)

        # if the player falls below the screen, they lose
        if player.pos[1] > HEIGHT:
            player.lost = True
    
    ################################################################################################################################################################
    # control movement
    ################################################################################################################################################################
    
    # make the player be affected by gravity
    player.apply_gravity(DT)
   
    collision = False

    # if the player collides with a platform, it will bounce upwards
    for platform in platforms:
        if platform.collided_width(player, screen) and player.vel[1] > 0:
            collision = True
            print("The player collided with a platform")
            player.land_on_platform(DT, platform)

    # move the player
    if not collision:
        player.move(DT)

    ################################################################################################################################################################
    # display everything
    #################################################################################################################################################################
    
    # Fill the background with DoodleJump color
    screen.fill((248, 239, 230))

    # display DoodleJump grid
    for y_pos in horizontal_lines:
        pg.draw.line(screen, (233, 225, 214), (0, y_pos), (WIDTH, y_pos))
    for x_pos in vertical_lines:
        pg.draw.line(screen, (233, 225, 214), (x_pos, 0), (x_pos, HEIGHT))

    # display all objects
    for platform in platforms:
        platform.display(screen)
    player.display(screen)

    # # display the player's high score on the starting screen
    # if not player.playing:
    #     line1 = my_font.render("High Score:", False, (0, 0, 0))
    #     line2 = my_font.render(str(player.high_score), False, (0, 0, 0))
    #     screen.blit(line1, (0.6*WIDTH, 0.066*HEIGHT))
    #     screen.blit(line2, (0.765*WIDTH, 0.133*HEIGHT))

    if playing:
        # display the current score
        text = my_font.render(str(int(player.score)), False, (0, 0, 0))
        screen.blit(text, (0.1*WIDTH, 0.066*HEIGHT))

    # update the screen
    pg.display.flip() 

# quit pygame when the game is not longer running
pg.quit() 