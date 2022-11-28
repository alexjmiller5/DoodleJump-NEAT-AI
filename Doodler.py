# Project: DoodleJump-NEAT-AI
# Authors: Alex Miller and Ruihang Liu
# Email: alexjmil@bu.edu and hrl@bu.edu
# File description (Doodler.py): creates a 
# class for the player of the game
import pygame as pg
from pygame.locals import RLEACCEL

class Doodler:
    def __init__(self, starting_pos):
        self.left_img = pg.image.load("leftdoodler.png").convert()
        self.left_img.set_colorkey((255, 255, 255), RLEACCEL) # get rid of the background
        self.right_img = pg.image.load("rightdoodler.png").convert()
        self.right_img.set_colorkey((255, 255, 255), RLEACCEL) # get rid of the background
        self.height = self.left_img.get_height()
        self.width = self.left_img.get_width()
        self.prev_pos = starting_pos
        self.pos = starting_pos
        self.vel = (0, 0)
        self.acc = (0, 0)
        self.score = 0
        self.facing_right = True

    def display(self, surf):
        if self.facing_right:
            surf.blit(self.right_img, self.pos)
        else:
            surf.blit(self.left_img, self.pos)

    def land_on_platform(self, dt, platform):
        self.vel = (self.vel[0], -0.03*dt)
        self.acc = (self.acc[0], 0)
        self.pos = (self.pos[0], platform.pos[1] - self.height)
        self.prev_pos = (self.pos[0], platform.pos[1] - self.height)

    def move(self, dt):
        self.prev_pos = self.pos
        self.pos = (self.pos[0] + self.vel[0]*dt, self.pos[1] + self.vel[1]*dt)
        self.vel = (self.vel[0] + self.acc[0]*dt, self.vel[1] + self.acc[1]*dt)

    def move_right(self, dt):
        self.facing_right = True
        self.acc = (.0001*dt, self.acc[1])
        if self.vel[0] > 0.02*dt:
            self.vel = (0.02*dt, self.vel[1])

    def move_left(self, dt):
        self.facing_right = False
        self.acc = (-.0001*dt, self.acc[1])
        if self.vel[0] < -0.02*dt:
            self.vel = (-0.02*dt, self.vel[1])