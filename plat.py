# Project: DoodleJump-NEAT-AI
# Authors: Alex Miller and Ruihang Liu
# Email: alexjmil@bu.edu and hrl@bu.edu
# File description (main.py): implements main
# functionality of the DoodleJump game using pygame

import pygame as pg
from pygame.locals import RLEACCEL
import random

class Platform():
    def __init__(self, pos, type):
        self.pos = pos
        self.img = pg.image.load(type + " platform.png").convert()
        self.img.set_colorkey((255, 255, 255), RLEACCEL) # get rid of the background
        self.height = self.img.get_height()
        self.width = self.img.get_width()
        self.type = type
        self.vel = random.random()*3 + 1.5

    def display(self, surf):
        """displays the platform on the input pygame surface
        """

        # display a box around the platform for testing purposes
        # l1p1 = (self.pos[0] - 15, self.pos[1] - 15)
        # l1p2 = (self.pos[0] - 15, self.pos[1] + 15 + self.height)
        # l2p1 = (self.pos[0] + self.width + 15, self.pos[1] - 15)
        # l2p2 = (self.pos[0] + self.width + 15, self.pos[1] + 15 + self.height)
        
        # pg.draw.line(surf, (0, 0, 0), l1p1, l2p1)
        # pg.draw.line(surf, (0, 0, 0), l2p2, l1p2)
        # pg.draw.line(surf, (0, 0, 0), l1p1, l1p2)
        # pg.draw.line(surf, (0, 0, 0), l2p1, l2p2)

        surf.blit(self.img, self.pos)

    def collided_width(self, player):
        """detect collsions between the line of direction of 
        the input position tuples, using the intersection of the
        lines that returning true if they collide and false if not
        """
        p1 = (self.pos[0] + self.width, self.pos[1] + self.height*0.1)
        p2 = (self.pos[0], self.pos[1] + self.height*0.1)
        p3 = ()
        p4 = ()
        p5 = ()
        p6 = ()
        

        if player.facing_right:
            p3 = (player.prev_pos[0] + 0.1*player.width, player.prev_pos[1] + player.height)
            p4 = (player.pos[0] + 0.1*player.width, player.pos[1] + player.height)
            p5 = (player.prev_pos[0] + 0.6*player.width, player.prev_pos[1] + player.height)
            p6 = (player.pos[0] + 0.6*player.width, player.pos[1] + player.height)
        else:
            p3 = (player.prev_pos[0] + 0.9*player.width, player.prev_pos[1] + player.height)
            p4 = (player.pos[0] + 0.9*player.width, player.pos[1] + player.height)
            p5 = (player.prev_pos[0] + 0.4*player.width, player.prev_pos[1] + player.height)
            p6 = (player.pos[0] + 0.4*player.width, player.pos[1] + player.height)


        # # draw the calculated lines for testing purposes
        # pg.draw.line(surf, (0, 0, 0), p1, p2)
        # pg.draw.line(surf, (0, 0, 0), p3, p4)
        # pg.draw.line(surf, (0, 0, 0), p5, p6)
        
        return intersect(p1, p2, p5, p6) or intersect(p1, p2, p3, p4)

    def in_view_of(self, doodler, screen_height):
        return self.pos[1] < doodler.score_line + 0.66*screen_height + self.height

    def is_too_close_to(self, other_plat, screen_width):
        """detects whether or not this platform is too close to another input
        platoform object
        """
        border_length = 1

        l1p1 = ()
        l1p2 = ()
        l2p1 = ()
        l2p2 = ()
        l3p1 = ()
        l3p2 = ()
        l4p1 = ()
        l4p2 = ()
        
        if self.type == "still" and other_plat.type == "still":
            l1p1 = (self.pos[0] - border_length, self.pos[1] - border_length)
            l1p2 = (self.pos[0] - border_length, self.pos[1] + border_length + self.height)
            l2p1 = (self.pos[0] + self.width + border_length, self.pos[1] - border_length)
            l2p2 = (self.pos[0] + self.width + border_length, self.pos[1] + border_length + self.height)

            l3p1 = (other_plat.pos[0] - border_length, other_plat.pos[1] - border_length)
            l3p2 = (other_plat.pos[0] + other_plat.width + border_length, other_plat.pos[1] - border_length)
            l4p1 = (other_plat.pos[0] - border_length, other_plat.pos[1] + border_length + other_plat.height)
            l4p2 = (other_plat.pos[0] + other_plat.width + border_length, other_plat.pos[1] + border_length + other_plat.height)

        else:
            l1p1 = (0, self.pos[1] - border_length)
            l1p2 = (screen_width, self.pos[1] - border_length)
            l2p1 = (0, self.pos[1] + border_length + self.height)
            l2p2 = (screen_width, self.pos[1] + border_length + self.height)

            l3p1 = (other_plat.pos[0] - border_length, other_plat.pos[1] - border_length)
            l3p2 = (other_plat.pos[0] - border_length, other_plat.pos[1] + border_length + other_plat.height)
            l4p1 = (other_plat.pos[0] + other_plat.width + border_length, other_plat.pos[1] - border_length)
            l4p2 = (other_plat.pos[0] + other_plat.width + border_length, other_plat.pos[1] + border_length + other_plat.height)
            
        return (intersect(l1p1, l1p2, l3p1, l3p2) or intersect(l1p1, l1p2, l4p1, l4p2) or intersect(l2p1, l2p2, l3p1, l3p2) or intersect(l2p1, l2p2, l4p1, l4p2))

    def move(self, screen_width):
        self.screen_wrap(screen_width)
        self.pos = (self.pos[0] + self.vel, self.pos[1])
    
    def screen_wrap(self, screen_width):
        if self.pos[0] > screen_width - self.width:
            self.pos = (screen_width - self.width, self.pos[1])
            self.vel = -self.vel
        if self.pos[0] < 0:
            self.pos = (0, self.pos[1])
            self.vel = -self.vel

def intersect(p1, p2, p3, p4):
    """helper function for the collsion detection, detects if two line segments intersect
    """
    return ccw(p1,p3,p4) != ccw(p2,p3,p4) and ccw(p1,p2,p3) != ccw(p1,p2,p4)

def ccw(p1, p2, p3):
    """helper function for the collsion detection
    """
    return (p3[1]-p1[1]) * (p2[0]-p1[0]) > (p2[1]-p1[1]) * (p3[0]-p1[0])