# Project: DoodleJump-NEAT-AI
# Authors: Alex Miller and Ruihang Liu
# Email: alexjmil@bu.edu and hrl@bu.edu
# File description (neat_doodler_5_inputs.py): 
#    this file implemented input option 2 mentioned in the paper we attached to this project.

import os
import neat

import pygame as pg

from Doodler import *
from plat import *

import time # to kill the current generation if one generation stuck)

class generation_counter():
    def __init__(self) -> None:
        self.generation = 0

    def increment(self):
        self.generation += 1

# fitness function for NEAT, will be called everytime a new generation starts
def eval_genomes(genomes, config):

    start_time = time.time()

    gen_counter.increment()

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

    dead_doodlers = []

    # Run until the user asks to quit
    running = True

    # for platform generation control
    prev_score = 0

    best_doodler_score_keeper = 0

    ####################################################################################################
    # neat-AI setup
    ####################################################################################################
    networks = []  # for all doodlers' neural network
    ge = []        # list for neat-python's genums
    doodlers = []  # each doodlers

    # list to holds the last highest-hiting platform for each player 
    hitPlatforms = []

    for _ in range(len(genomes)):
        hitPlatforms.append(platforms[0])

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
    
    # Run until the user asks to quit
    while True:

        # this will standardize speeds based on framerate
        clock.tick(FRAME_RATE)

        # Event handling
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()

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
        # platform generation as the best doodler gets higher and higher
        ################################################################################################################################################################

        # deteremine the chance a platform might be moving based on the doodler's score
        moving_chance = (best_doodler.score**0.5)/100

        # create platforms that are always reachable by the doodler
        if int(best_doodler.score) % 240 == 0 and int(best_doodler.score) != prev_score:
            new_plat_type = "still"
            if random.random() < moving_chance:
                new_plat_type = "moving"
            platforms.append(Platform((random.random()*(WIDTH - plat_width), best_doodler.score - 30), new_plat_type))
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
        # control doodler scores and loss condition
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
        # wrap the doodlers' position around the screen
        ################################################################################################################################################################
        
        # for doodler in doodlers:
        #     doodler.screen_wrap(WIDTH)

        #     for doodler in doodlers:
        #         if doodler.pos[0] > WIDTH:
        #             doodler.pos = (-doodler.width, doodler.pos[1])
        #         if doodler.pos[0] < -doodler.width:
        #             doodler.pos = (WIDTH, doodler.pos[1])

        # make the player be affected by gravity
        for doodler in doodlers:
            doodler.apply_gravity(DT)
            doodler.collision = False
        
        # if a doodler collides with a platform, it will bounce upwards
        for platform_id, platform in enumerate(platforms):
            for player_id, doodler in enumerate(doodlers):
                if platform.in_view_of(doodler, HEIGHT) and platform.collided_width(doodler) and doodler.vel[1] > 0:
                    doodler.collision = True
                    doodler.land_on_platform(DT, platform)

                    # print(platform.pos[1], hitPlatforms[player_id].pos[1])
                
                    # reward player for hitting higher platform
                    if platform.pos[1] < hitPlatforms[player_id].pos[1]:

                        # print("rewarding player {}".format(player_id))
                        # print(ge[player_id].fitness, ge[player_id].fitness + 0.1)
                        # print()
                        ge[player_id].fitness += 1

                        # also update hitPlatforms
                        hitPlatforms[player_id] = platform
                    
                    elif platform == hitPlatforms[player_id]:
                        # punish player for hitting same platform
                        # need to punish those m**f hard so they LEARN!!
                        # print("punishing player {} for hitting same platform".format(player_id))
                        # print(ge[player_id].fitness, ge[player_id].fitness - 0.05)
                        # print()
                        ge[player_id].fitness -= 5

        # move the player
        for doodler in doodlers:
            if not doodler.collision:
                doodler.move(DT)

        pg.draw.line(screen, (0,0,0), (0,worst_doodler.pos[1] - HEIGHT*0.5 - plat_height), (WIDTH,worst_doodler.pos[1] - HEIGHT*0.5 - plat_height))
        for platform in platforms:
            if platform.pos[1] > worst_doodler.pos[1] + HEIGHT*0.66 + plat_height:
                platforms.remove(platform)

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
        
        # display all doodlers
        for doodler in doodlers:
            if doodler.pos[1] < HEIGHT + doodler.height:
                doodler.display(screen)

        # display the best fitness
        fit_list = []
        for g in ge:
            fit_list.append(g.fitness)
        best_fitness = my_font.render("best_fitness: " + str(max(fit_list)), False, (0, 0, 0))

        screen.blit(best_fitness, (0.1*WIDTH, 0.066*HEIGHT))

        # display the best doodler's score
        score = my_font.render("best score: " + str(int(best_doodler.score)), False, (0, 0, 0))
        screen.blit(score, (0.1*WIDTH, 0.1*HEIGHT))

        gen_text = my_font.render("Generation: " + str(gen_counter.generation), False, (0, 0, 0))
        screen.blit(gen_text, (0.1*WIDTH, 0.18*HEIGHT))

        # update the screen
        pg.display.flip() 

        # reward the living doodlers
        # for player_id, player in enumerate(doodlers):
        #     if player not in dead_doodlers:
        #         ge[player_id].fitness += 0.1

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

            # calculate the relative distance between doodler and those platforms
            cloest_platform_above_dist_x = player_x - cloest_platform_above_x
            cloest_platform_above_dist_y = player_y - cloest_platform_above_y

            cloest_platform_below_dist_x = player_x - cloest_platform_below_x
            cloest_platform_below_dist_y = cloest_platform_below_y - player_y

            #feed the networks
            output = networks[player_id].activate((cloest_platform_above_dist_x, cloest_platform_above_dist_y, 
                                                    cloest_platform_below_dist_x, cloest_platform_below_dist_y,
                                                    player.vel[1]))

            if output[0] > 0.5:
                player.update_movement(DT, True, False)
            if output[1] > 0.5:
                player.update_movement(DT, False, True)

        # draw out the red lines
        pg.display.flip() 

        # update best_doodler_score_keeper every 5 seconds
        if int(time.time() - start_time) % 5 == 0:
            # update score keeper as well
            best_doodler_score_keeper = int(best_doodler.score)

        # check every 10 seconds
        # if the best doodler survive without actually increase the score
        # it probably doing-back-and-forth movement
        # kill the generation
        # did plus 1 so the game doesn't quit right at launch
        if int(time.time() + 1 - start_time) % 10 == 0 and best_doodler_score_keeper == int(best_doodler.score):
            pg.quit()
            break

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

    winner = population.run(eval_genomes, 100)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, '../config/config-5.txt')

    gen_counter = generation_counter()

    run(config_path)