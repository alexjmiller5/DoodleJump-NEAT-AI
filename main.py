# Project: DoodleJump-NEAT-AI
# Authors: Alex Miller and Ruihang Liu
# Email: alexjmil@bu.edu and hrl@bu.edu
# File description (main.py): implements main
# functionality of the DoodleJump game using pygame

import pygame as pg
from Doodler import Doodler
from plat import Platform
import random

pg.init()
pg.display.init()

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

# store platform dimension variables
temp_plat = Platform((0,0), "still")
plat_width = temp_plat.width
plat_height = temp_plat.height

# NEAT variables
GENERATION_SIZE = 100

# initialize object lists
platforms = []
doodlers = [Doodler((WIDTH/2, 0.9*HEIGHT)) for i in range(GENERATION_SIZE)]
dead_doodlers = []

platforms.append(Platform((WIDTH/2, HEIGHT - 50), "still"))

# NEAT variables
GENERATION_SIZE = 20

# initialize object lists
platforms = []
doodlers = [Doodler((WIDTH/2, 0.9*HEIGHT)) for i in range(GENERATION_SIZE)]
dead_doodlers = []

platforms.append(Platform((WIDTH/2, HEIGHT - 50), "still"))

# generate initial platforms
while len(platforms) <= 10:
    new_plat_pos = (random.random()*(WIDTH - plat_width), random.random()*(HEIGHT - 2*plat_height) - plat_height - 40)
    new_plat = Platform(new_plat_pos, "still")
    is_too_close = False
    for platform in platforms:
        if new_plat.is_too_close_to(platform, WIDTH):
            is_too_close = True
    if not is_too_close:
        platforms.append(new_plat)

# set initial doodler variables
for doodler in doodlers:
    doodler.vel = (0, -0.025*DT)
    doodler.score_line = 0.33*HEIGHT

# for platform generation control
prev_score = 0

# Run until the user asks to quit
while True:

    # this will standardize speeds based on framerate
    clock.tick(FRAME_RATE)

    # necessary to quit pygame correctly
    for event in pg.event.get():
        if event.type == pg.QUIT:
            quit()

    # Detemine the best and worst doodlers based on their scores
    best_doodler = doodlers[0]
    worst_doodler = doodlers[0]
    for doodler in doodlers:
        if doodler.score > best_doodler.score:
            best_doodler = doodler
        if doodler.score < worst_doodler.score:
            worst_doodler = doodler

    ################################################################################################################################################################
    # scroll screen back to the best doodler in case it's much lower than the previous best doodler
    ################################################################################################################################################################

    if best_doodler.score_line > 0.33*HEIGHT:
        offset = best_doodler.score_line - 0.33*HEIGHT
        best_doodler.score_line = 0.33*HEIGHT
        for doodler in doodlers:
            doodler.pos = (doodler.pos[0], doodler.pos[1] - offset)
            doodler.score_line -= offset
        for platform in platforms:
            platform.pos = (platform.pos[0], platform.pos[1] - offset)

    ################################################################################################################################################################
    # Move the doodlers based on the AI
    ################################################################################################################################################################

    for doodler in doodlers:
        doodler.ai_random_move(DT)

    ################################################################################################################################################################
    # platform generation as the best doodler gets higher and higher
    ################################################################################################################################################################

    # deteremine the chance a platform might be moving based on the doodler's score
    moving_chance = (best_doodler.score**0.5)/100

    # create platforms that are always reachable by the doodler
    if int(best_doodler.score) % 240 == 0 and int(best_doodler.score) != prev_score:
        new_plat_type = "still"
        if random.random() < moving_chance:
            new_plat_type = "moving"
        platforms.append(Platform((random.random()*(WIDTH - plat_width), best_doodler.score + 30), new_plat_type))
        prev_score = int(best_doodler.score)

    # keep track of the number of platforms that will be put on the screen
    # this number will decrease as the player's score gets higher and eventually reach 0
    doodler_change = (worst_doodler.score_line + HEIGHT)/HEIGHT
    extra_platform_num = int((10 - (best_doodler.score/20)**0.1)*doodler_change)

    # add the extra platforms to the screen where possible
    tries = 0
    while len(platforms) - 4 <= extra_platform_num:
        if tries > 10:
            break
        new_plat_pos = (random.random()*(WIDTH - plat_width), -1*plat_height - 20 - random.random()*HEIGHT)
        new_plat_type = "still"
        if random.random() < 0.1:
            new_plat_type = "moving"
        new_plat = Platform(new_plat_pos, new_plat_type)
        is_too_close = False
        for platform in platforms:
            if new_plat.is_too_close_to(platform, WIDTH):
                is_too_close = True
        if not is_too_close:
            platforms.append(Platform(new_plat_pos, new_plat_type))
            tries = 0
        tries += 1

    ################################################################################################################################################################
    # scroll the game upwards as the best doodler gets higher and higher
    ################################################################################################################################################################

    if best_doodler.pos[1] < 0.33*HEIGHT and best_doodler.vel[1] < 0:
        offset = best_doodler.vel[1]
        for doodler in doodlers:
            if doodler != best_doodler:
                doodler.pos = (doodler.pos[0], doodler.pos[1] - offset*DT)
                doodler.score_line -= offset*DT
        best_doodler.score -= offset*DT
        best_doodler.pos = (best_doodler.pos[0], best_doodler.pos[1] - offset*DT)
        for platform in platforms:
            platform.pos = (platform.pos[0], platform.pos[1] - offset*DT)

    ################################################################################################################################################################
    # control doodler scores
    ################################################################################################################################################################

    for doodler in doodlers:
        offset = doodler.vel[1]
        if doodler.pos[1] < doodler.score_line and offset < 0 and doodler != best_doodler:
            doodler.score -= offset*DT
            doodler.score_line += offset*DT

    ################################################################################################################################################################
    # control doodler loss condition
    ################################################################################################################################################################

    for doodler in doodlers:
        if doodler.is_dead(HEIGHT):
            dead_doodlers.append(doodler)
            doodlers.remove(doodler)
    
    if len(doodlers) == 0:
        quit()
        break

    ################################################################################################################################################################
    # remove platforms that are below the doodler with the lowest score
    ################################################################################################################################################################
    
    for platform in platforms:
        if platform.pos[1] > worst_doodler.pos[1] + HEIGHT*0.66 + plat_height:
            platforms.remove(platform)

    ################################################################################################################################################################
    # control moving platform movement
    ################################################################################################################################################################

    for platform in platforms:
        if platform.type == "moving":
            platform.move(WIDTH)

    ################################################################################################################################################################
    # control doodler movement
    ################################################################################################################################################################
    
    # wrap the doodlers' position around the screen
    for doodler in doodlers:
        doodler.screen_wrap(WIDTH)

    # make the player be affected by gravity
    for doodler in doodlers:
        doodler.apply_gravity(DT)
        doodler.collision = False

    # if a doodler collides with a platform, it will bounce upwards
    for platform in platforms:
        for doodler in doodlers:
            if platform.in_view_of(doodler, HEIGHT) and platform.collided_width(doodler) and doodler.vel[1] > 0:
                doodler.collision = True
                doodler.land_on_platform(DT, platform)

    # move the player
    for doodler in doodlers:
        doodler.move(DT)

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

    # display all platforms
    for platform in platforms:
        platform.display(screen)
    
    # display all doodlers
    for doodler in doodlers:
        if doodler.pos[1] < HEIGHT + doodler.height:
            doodler.display(screen)

    # display the best doodler's score
    text = my_font.render(str(int(best_doodler.score)), False, (0, 0, 0))
    screen.blit(text, (0.1*WIDTH, 0.066*HEIGHT))

    # update the screen
    pg.display.flip()