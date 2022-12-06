import os
import neat

import pygame as pg
import random

from Doodler import Doodler
from plat import Platform

# fitness function for NEAT, will be called everytime a new generation starts
def eval_genomes(genomes, config):

    ####################################################################################################
    # game setup portion from main with modification:
    ####################################################################################################
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

    # initialize object lists
    platforms = []
    dead_doodlers = []

    # generate initial platforms
    platforms.append(Platform((WIDTH/2, HEIGHT - 50), "still"))
    while len(platforms) <= 10:
        new_plat_pos = (random.random()*(WIDTH - plat_width), random.random()*(HEIGHT - 2*plat_height) - plat_height - 40)
        new_plat = Platform(new_plat_pos, "still")
        is_too_close = False
        for platform in platforms:
            if new_plat.is_too_close_to(platform, WIDTH):
                is_too_close = True
        if not is_too_close:
            platforms.append(new_plat)

    # Run until the user asks to quit
    running = True

    # for platform generation control
    prev_score = 0

    ####################################################################################################
    # neat-AI setup
    ####################################################################################################
    networks = []  # for all doodlers' neural network
    ge = []        # list for neat-python's genums
    doodlers = []  # each doodlers

    # list which holds the index of the last hiting platform for each player 
    hitPlatforms = []

    # number of iteration will base on POP_SIZE in the configuration file
    for genome_id, genome in genomes: 
        genome.fitness = 0  # start with fitness level of 0
        network = neat.nn.FeedForwardNetwork.create(genome, config) # create a network for the genome
        networks.append(network)
        ge.append(genome)

        doodler = Doodler((WIDTH/2, 0.9*HEIGHT))
        doodler.vel = (0, -0.025*DT)
        doodler.score_line = 0.33*HEIGHT

        doodlers.append(doodler)
        hitPlatforms.append(0)
    
    while running:

        # this will standardize speeds based on framerate
        clock.tick(FRAME_RATE)

        # Event handling
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                pg.quit()
                quit()
                break
                

        # find the best and worst doodler
        # best doodler for the platform generation and spotlight
        # worst doodler for removing the platform (so less RAM need and program don't become too big and crash)
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
        # platform generation as the best doodler gets higher and higher
        ################################################################################################################################################################

        # deteremine the chance a platform might be moving based on the doodler's score
        moving_chance = (best_doodler.score**0.5)/100

        # create platforms that are always reachable by the doodler
        if int(best_doodler.score) % 240 == 0 and int(best_doodler.score) != prev_score:
            new_plat_type = "still"
            if random.random() < moving_chance:
                new_plat_type = "moving"
            platforms.append(Platform((random.random()*(WIDTH - plat_width), - HEIGHT - 100), new_plat_type))
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
            pg.quit()
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

        # make the doodlers be affected by gravity
        for doodler in doodlers:
            doodler.apply_gravity(DT)
            doodler.collision = False

        # if a doodler collides with a platform, it will bounce upwards
        for platform_id, platform in enumerate(platforms):
            for player_id, doodler in enumerate(doodlers):
                if platform.pos[1] > doodler.score_line - 0.5*HEIGHT - platform.height:
                    if platform.collided_width(doodler) and doodler.vel[1] > 0:
                        doodler.collision = True
                        doodler.land_on_platform(DT, platform)

                        # update hitPlatforms
                        hitPlatforms[player_id] = platform_id
                    elif platform.collided_width(doodler):
                        # reward player for hitting higher platform
                        if platform_id > hitPlatforms[player_id]:
                            ge[player_id].fitness += 1
                        
                        # punish player for hitting lower platform
                        if  platform_id < hitPlatforms[player_id]:
                            ge[player_id].fitness -= 0.5

                        hitPlatforms[player_id] = platform_id

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

        # reward the living doodlers
        for player_id, player in enumerate(doodlers):
            if player not in dead_doodlers:
                ge[player_id].fitness += 1

        for player_id, player in enumerate(doodlers):
            # Variables for Input layer

            # calculate the distance between 
            player_x, player_y = player.pos

            cloest_platform_above_x = 0
            cloest_platform_above_y = 0
            cloest_platform_above_dist = float("inf")

            cloest_platform_below_x, cloest_platform_below_y = platforms[-1].pos
            cloest_platform_below_dist = float("inf")

            for platform in platforms:
                platform_x, platform_y = platform.pos

                dist = (player_x - platform_x)**2 + (player_y - platform_y)**2

                # platform is above and is closer than current cloest
                if platform_y < player_y and dist < cloest_platform_above_dist:
                    # replace cloest_platform_above
                    cloest_platform_above_x = platform_x
                    cloest_platform_above_y = platform_y
                    cloest_platform_above_dist = dist
                
                # platform is below and is closer than current cloest
                if platform_y > player_y and dist < cloest_platform_below_dist:
                    # replace cloest_platform_below
                    cloest_platform_below_x = platform_x
                    cloest_platform_below_y = platform_y
                    cloest_platform_below_dist = dist

            cloest_platform_above = (cloest_platform_above_x, cloest_platform_above_y)
            cloest_platform_below = (cloest_platform_below_x, cloest_platform_below_y)

            # display the input on-screen so we can see the learning process
            pg.draw.line(screen, (255, 0, 0), player.pos, cloest_platform_above)
            pg.draw.line(screen, (255, 0, 0), player.pos, cloest_platform_below)

            #feed the networks
            output = networks[player_id].activate((cloest_platform_above_x, cloest_platform_above_y, 
                                                    cloest_platform_below_x, cloest_platform_below_y,
                                                    player_x, player_y, player.vel[1]))

            if output[0] > 0.5:
                player.move_left(DT)
            if output[1] > 0.5:
                player.move_right(DT)

        # draw out the red lines
        pg.display.flip() 

def run(config_file):
    # start the neat algorithm based on the congifuration file
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    
    population = neat.Population(config)
    
    # use neat's defailt generation report to show us the progress in terminal
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Run for up to 50 generations.
    # eval_genomes is the fitness function which is called once per generation
    print("about to start")

    winner = population.run(eval_genomes, 50)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)