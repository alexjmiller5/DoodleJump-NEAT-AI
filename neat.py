
import os
import neat
import random

import pygame
from Doodler import *
from plat import *


WIDTH = 493 # Screen width constant
HEIGHT = int(WIDTH*1.5) # Screen height constant

# initialize pygame fonts
pg.font.init()
my_font = pg.font.SysFont('Comic Sans MS', 30)

# where to print the lines in the grid onscreen
vertical_lines = [i for i in range(WIDTH) if i % 20 == 0]
horizontal_lines = [i for i in range(HEIGHT) if i % 20 == 0]

# get platform width
platform_img = pg.image.load("platform.png").convert()
platform_img.set_colorkey((255, 255, 255), RLEACCEL) # get rid of the background
plat_width = platform_img.get_width()


# fitness function for NEAT, will be called everytime a new generation starts
def eval_genomes(genomes, config):

    ####################################################################################################
    # neat-AI setup
    ####################################################################################################
    networks = []  # for all doodlers' neural network
    ge = []        # list for neat-python's genums
    doodlers = []  # each doodlers

    # number of iteration will base on POP_SIZE in the configuration file
    for genome_id, genome in genomes: 
        genome.fitness = 0  # start with fitness level of 0
        network = neat.nn.FeedForwardNetwork.create(genome, config) # create a network for the genome
        networks.append(network)
        doodlers.append(Doodler(((WIDTH*0.12, HEIGHT*0.8 - 100))))
        ge.append(genome)

    hit_platform = []  # list which holds the index of the last hiting platform for each player 

    ####################################################################################################
    # game setup portion from main with modification:
    ####################################################################################################
    pg.init()
    # initialize the framerate object and clock so that we can standardize framerate
    clock = pg.time.Clock()
    FRAME_RATE = 60
    DT = (1200/FRAME_RATE)

    # Set up the drawing window
    screen = pg.display.set_mode([WIDTH, HEIGHT])
    pg.display.set_caption("Doodle Jump!")

    ####################################################################################################
    # The game portion from main with modification:
    ####################################################################################################

    # boolean variable to keep track of the game state
    playing = False

    # Run until the user asks to quit
    running = True

    # for platform generation control
    prev_score = 0

    # initialize objects
    platforms = []
    platforms.append(Platform((random.random()*(WIDTH - plat_width), -100)))
    
    while running and len(doodlers) > 0:

        # this will standardize speeds based on framerate
        clock.tick(FRAME_RATE)

        # Event handling
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                pg.quit()
                quit()
                break
            
        # create the starting when the user starts playing
        if not playing:
            
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
            for player in doodlers:
                player.prev_pos = (WIDTH*0.12, HEIGHT*0.8 - 100)
                player.pos = (WIDTH/2, 0.9*HEIGHT)
                player.vel = (player.vel[0], -0.025*DT)
                player.acc = (0, 0)
            playing = True

        # work the functionality for the screen when the user has started the game
        if playing:

            # generate platforms
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
                new_plat = plat.Platform(new_plat_pos)
                is_too_close = False
                for platform in platforms:
                    if new_plat.is_too_close_to(platform):
                        is_too_close = True
                if not is_too_close:
                    platforms.append(plat.Platform(new_plat_pos))
                    tries = 0
                tries += 1

            for player_id, player in enumerate(doodlers):

                #Var. for Input layer
                # I am thinking about having the input being the next cloest platform
                # so variable name: nextPlat_right, nextPlat_left, nextPlat_hight, play_place
                
                #feed the networks with myplace, next obstacle distance, next obstacle hight, next obstacle widht of each player
                
                # output = networks[player_id].activate((nextPlat_right, nextPlat_left, nextPlat_hight, myPlace))
                pass


    pass


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
    winner = population.run(eval_genomes, 50)


if __name__ == "main":
    current_path = os.path.dirname(__file__)
    config_path = os.path.join(current_path, 'config-feedforward.txt')
    # run(config_path)