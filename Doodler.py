# Project: DoodleJump-NEAT-AI
# Authors: Alex Miller and Ruihang Liu
# Email: alexjmil@bu.edu and hrl@bu.edu
# File description (Doodler.py): creates a 
# class for the player of the game
import pygame as pg
from pygame.locals import RLEACCEL

class Doodler:
    def __init__(self, starting_pos):
        self.img = pg.image.load("doodler.png").convert()
        self.img.set_colorkey((255, 255, 255), RLEACCEL) # get rid of the background
        self.height = self.img.get_height()
        self.width = self.img.get_width()
        self.prev_pos = starting_pos
        self.pos = starting_pos
        self.vel = (0, 0)
        self.acc = (0, 0)
        self.score = 0

    def display(self, surf):
        surf.blit(self.img, self.pos)

    def move(self, dt):
        self.prev_pos = self.pos
        self.pos = (self.pos[0] + self.vel[0]*dt, self.pos[1] + self.vel[1]*dt)
        self.vel = (self.vel[0] + self.acc[0]*dt, self.vel[1] + self.acc[1]*dt)

    def move_right(self):
        self.pos = (self.pos[0] + 5.5, self.pos[1])

    def move_left(self):
        self.pos = (self.pos[0] - 5.5, self.pos[1])