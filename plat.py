# Project: DoodleJump-NEAT-AI
# Authors: Alex Miller and Ruihang Liu
# Email: alexjmil@bu.edu and hrl@bu.edu
# File description (main.py): implements main
# functionality of the DoodleJump game using pygame

import pygame as pg
from pygame.locals import RLEACCEL

class Platform():
    def __init__(self, pos):
        self.pos = pos
        self.img = pg.image.load("platform.png").convert()
        self.img.set_colorkey((255, 255, 255), RLEACCEL) # get rid of the background
        # self.img = pg.Surface((20, 10))
        self.height = self.img.get_height()
        self.width = self.img.get_width()

    def display(self, surf):
        """displays the platform on the input pygame surface
        """
        surf.blit(self.img, self.pos)

    def collided_width(self, player):
        """detect collsions between the line of direction of 
        the input position tuples, using the intersection of the
        lines that returning true if they collide and false if not
        """
        p1 = (self.pos[0] + 0.5*self.width, self.pos[1] - self.height)
        p2 = (self.pos[0] - 0.5*self.width, self.pos[1] - self.height)
        p3 = player.prev_pos
        p4 = player.pos

        # print(p1, p2)
        
        return ccw(p1,p3,p4) != ccw(p2,p3,p4) and ccw(p1,p2,p3) != ccw(p1,p2,p4)

def ccw(p1, p2, p3):
    """helper function for the collsion detection
    """
    return (p3[1]-p1[1]) * (p2[0]-p1[0]) > (p2[1]-p1[1]) * (p3[0]-p1[0])