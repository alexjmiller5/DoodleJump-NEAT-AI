# Project: DoodleJump-NEAT-AI
# Authors: Alex Miller and Ruihang Liu
# Email: alexjmil@bu.edu and hrl@bu.edu
# File description (main.py): implements main
# functionality of the DoodleJump game using pygame

import pygame as pg
import random

class Platform():
    def __init__(self, pos):
        self.pos = pos
        self.img = pg.image.load("platform.png").convert()
        # self.img = pg.Surface((20, 10))
        self.height = self.img.get_height()
        self.width = self.img.get_width()
    
    def display(self, surf):
        surf.blit(self.img, self.pos)

    def collided_width(prev_pos, pos):
        