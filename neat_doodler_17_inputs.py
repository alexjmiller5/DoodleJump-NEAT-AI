import os
import neat

import pygame as pg

from Doodler import *
from plat import *

import math

import time # to kill the current generation if one generation stuck)

class generation_counter():
    def __init__(self) -> None:
        self.generation = 0

    def increment(self):
        self.generation += 1

# fitness function for NEAT, will be called everytime a new generation starts
def eval_genomes(genomes, config):

    gen_counter.increment()

    start_time = time.time()

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
        
        # don't wrap the doodler to make learning faster
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
                        # print(ge[player_id].fitness, ge[player_id].fitness + 1)
                        # print()
                        ge[player_id].fitness += 1

                        # also update hitPlatforms
                        hitPlatforms[player_id] = platform
                    
                    elif platform == hitPlatforms[player_id]:
                        # punish player for hitting same platform
                        # need to punish those m**f hard so they LEARN!!
                        # print("punishing player {} for hitting same platform".format(player_id))
                        # print(ge[player_id].fitness, ge[player_id].fitness - 5)
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

        lines_to_draw = []

        for player_id, player in enumerate(doodlers):
            # Variables for Input layer

            possible_output_plats = [[], [], [], [], [], [], [], []]

            player_lines = []
            for degrees in range(0, 360, 45):
                radians = degrees*math.pi/180
                new_line_p1 = (HEIGHT*math.cos(radians) + player.pos[0], HEIGHT*math.sin(radians) + player.pos[1])
                new_line_p2 = (player.pos[0] + 0.5*player.width*(1 + math.cos(radians)), player.pos[1] + 0.5*player.height*(1 + math.sin(radians)))
                new_line = (new_line_p1, new_line_p2)
                player_lines.append(new_line)

            for platform in platforms:
                plat_lines = platform.get_rect()
                for plat_line in plat_lines:
                    for i in range(8):
                        player_line = player_lines[i]
                        
                        # draw lines for testing
                        # if player == best_doodler:
                            # pg.draw.line(screen, (255, 0, 0), plat_line[0], plat_line[1])
                            # pg.draw.line(screen, (255, 0, 0), player_line[0], player_line[1])
                        if intersect(plat_line[0], plat_line[1], player_line[0], player_line[1]):
                            possible_output_plats[i].append(platform)

            output_plats = [0]*8

            for i in range(8):
                plats = possible_output_plats[i]
                closest_plat = None
                closest_plat_dist = float("inf")
                for plat in plats:
                    temp_dist = dist(player.pos, plat.pos)
                    if temp_dist < closest_plat_dist:
                        closest_plat = plat
                        closest_plat_dist = temp_dist
                output_plats[i] = closest_plat
            
            output_x_and_y_dists = []

            for i in range(8):
                plat = output_plats[i]
                if plat != None:
                    if player == best_doodler:
                        lines_to_draw.append(((player.pos[0] + 0.5*player.height, player.pos[1] + 0.5*player.width), (plat.pos[0] + 0.5*plat.width, plat.pos[1] + 0.5*plat.height)))
                    output_x_and_y_dists.append((plat.pos[0] - player.pos[0], plat.pos[1] - player.pos[1]))
                else:
                    radians = i*math.pi/4
                    output_x_and_y_dists.append((0, 0))
                    # output_x_and_y_dists.append((-1000000000*math.cos(radians), -1000000000*math.sin(radians)))

            moving_up = player.vel[1] > 0

            output = networks[player_id].activate((
            output_x_and_y_dists[0][0], 
            output_x_and_y_dists[0][1], 
            output_x_and_y_dists[1][0],
            output_x_and_y_dists[1][1],
            output_x_and_y_dists[2][0],
            output_x_and_y_dists[2][1],
            output_x_and_y_dists[3][0],
            output_x_and_y_dists[3][1],
            output_x_and_y_dists[4][0],
            output_x_and_y_dists[4][1],
            output_x_and_y_dists[5][0],
            output_x_and_y_dists[5][1],
            output_x_and_y_dists[6][0],
            output_x_and_y_dists[6][1],
            output_x_and_y_dists[7][0],
            output_x_and_y_dists[7][1],
            moving_up
            ))

            if output[0] > 0.5:
                player.update_movement(DT, True, False)
            if output[1] > 0.5:
                player.update_movement(DT, False, True)

        # draw the red lines (the doodler's line of sight to the platforms) for the best doodler
        for line in lines_to_draw:
            pg.draw.line(screen, (255, 0, 0), line[0], line[1])

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

def dist(p1, p2):
    return math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )

if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-17.txt')

    gen_counter = generation_counter()

    run(config_path)