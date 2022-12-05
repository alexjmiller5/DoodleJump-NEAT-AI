import os
import neat

import pygame as pg

from Doodler import *
from plat import *

# fitness function for NEAT, will be called everytime a new generation starts
def eval_genomes(genomes, config):

    print("eval_genomes called")

    ####################################################################################################
    # game setup portion from main with modification:
    ####################################################################################################
    pg.init()

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

    # initialize objects
    platforms = []
    temp_plat = Platform((0,0))
    plat_width = temp_plat.width
    plat_height = temp_plat.height

    # generate initial platforms
    while len(platforms) <= 30:
        new_plat_pos = (random.random()*(WIDTH - plat_width), random.random()*(HEIGHT - 2*plat_height) - plat_height - 40)
        new_plat = Platform(new_plat_pos)
        is_too_close = False
        for platform in platforms:
            if new_plat.is_too_close_to(platform):
                is_too_close = True
        if not is_too_close:
            platforms.append(Platform(new_plat_pos))

    dead_doodlers = []

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
        # platform generation as the best doodler gets higher and higher
        ################################################################################################################################################################

        # create platforms that are always reachable by the doodler
        if int(best_doodler.score) % 17 == 0 and int(best_doodler.score) != prev_score:
            platforms.append(Platform((random.random()*(WIDTH - plat_width), -100)))
            prev_score = int(best_doodler.score)

        # keep track of the number of platforms that will be put on the screen
        # this number will decrease as the player's score gets higher and eventually reach 0
        doodler_change = (worst_doodler.score_line + HEIGHT)/HEIGHT
        extra_platform_num = int((30 - best_doodler.score**0.5)*doodler_change)

        tries = 0
        while len(platforms) - 4 <= extra_platform_num:
            if tries > 10:
                break
            new_plat_pos = (random.random()*(WIDTH - plat_width), -1*plat_height - 20 - random.random()*HEIGHT)
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
        # scroll the game upwards as the best doodler gets higher and higher
        ################################################################################################################################################################

        if best_doodler.pos[1] < 0.33*HEIGHT and best_doodler.vel[1] < 0:
            offset = best_doodler.vel[1]
            for doodler in doodlers:
                if doodler != best_doodler:
                    doodler.pos = (doodler.pos[0], doodler.pos[1] - offset*DT)
                    doodler.score_line -= offset
            best_doodler.score -= offset
            best_doodler.pos = (best_doodler.pos[0], best_doodler.pos[1] - offset*DT)
            for platform in platforms:
                platform.pos = (platform.pos[0], platform.pos[1] - offset*DT)

        ################################################################################################################################################################
        # control doodler scores and loss condition
        ################################################################################################################################################################

        for doodler in doodlers:
            offset = doodler.vel[1]
            if doodler.pos[1] < doodler.score_line and offset < 0:
                doodler.score -= offset
                doodler.score_line += offset
        
        for doodler in doodlers:
            if doodler.pos[1] > doodler.score_line + 0.66*HEIGHT + doodler.height:
                dead_doodlers.append(doodler)
                doodler.dead = True
                doodlers.remove(doodler)

        if len(doodlers) == 0:
            pg.quit()
            break

        ################################################################################################################################################################
        # wrap the doodlers' position around the screen
        ################################################################################################################################################################
        
        for doodler in doodlers:
            if doodler.pos[0] > WIDTH:
                doodler.pos = (-doodler.width, doodler.pos[1])
            if doodler.pos[0] < -doodler.width:
                doodler.pos = (WIDTH, doodler.pos[1])

        
        ################################################################################################################################################################
        # control movement
        ################################################################################################################################################################
        
        # make the player be affected by gravity
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
        
        for doodler in doodlers:
            if doodler.pos[1] < HEIGHT + doodler.height:
                doodler.display(screen)

        # display the current score
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
            # I am thinking about having the input being the next cloest platform

            try:
                next_platform = platforms[hitPlatforms[player_id]+1]
            except:
                print(player_id)
                print(hitPlatforms[player_id])
                print(len(platforms))

            # calculate the distance between 
            next_platform_x, next_platform_y = next_platform.pos
            player_x, player_y = player.pos

            x_distance = next_platform_x - player_x
            y_distance = next_platform_y - player_y

            # display out the distance using red line so we can see the actual process
            pg.draw.line(screen, (255, 0, 0), player.pos, next_platform.pos)

            #feed the networks with myplace, next obstacle distance, next obstacle hight, next obstacle widht of each player
            
            output = networks[player_id].activate((x_distance, y_distance))

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