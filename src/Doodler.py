# Project: DoodleJump-NEAT-AI
# Authors: Alex Miller and Ruihang Liu
# Email: alexjmil@bu.edu and hrl@bu.edu
# File description (Doodler.py): creates a 
# class for the player of the game
import pygame as pg
import random
from pygame.locals import RLEACCEL

class Doodler:
    def __init__(self, starting_pos):
        self.left_img = pg.image.load("../assets/images/leftdoodler.png").convert()
        self.left_img.set_colorkey((255, 255, 255), RLEACCEL) # get rid of the background
        self.right_img = pg.image.load("../assets/images/rightdoodler.png").convert()
        self.right_img.set_colorkey((255, 255, 255), RLEACCEL) # get rid of the background
        self.height = self.left_img.get_height()
        self.width = self.left_img.get_width()
        self.prev_pos = starting_pos
        self.pos = starting_pos
        self.vel = (0, 0)
        self.acc = (0, 0)
        self.score = 1
        self.gravity = 0.0000025
        self.facing_right = True
        self.lost = False
        self.score_line = 0
        self.collision = False
        self.start_movement = False

    def display(self, surf):
        if self.facing_right:
            surf.blit(self.right_img, self.pos)
        else:
            surf.blit(self.left_img, self.pos)

    def land_on_platform(self, dt, platform):
        self.vel = (self.vel[0], -0.03*dt*(self.score**0.05))
        self.acc = (self.acc[0], 0)
        self.pos = (self.pos[0], platform.pos[1] - self.height)
        self.prev_pos = (self.pos[0], platform.pos[1] - self.height)

    def move(self, dt):
        if not self.collision:
            self.prev_pos = self.pos
            self.pos = (self.pos[0] + self.vel[0]*dt, self.pos[1] + self.vel[1]*dt)
            self.vel = (self.vel[0] + self.acc[0]*dt, self.vel[1] + self.acc[1]*dt)

    def apply_gravity(self, dt):
        self.acc = (self.acc[0], self.acc[1] + self.gravity*dt*(self.score**0.1))

    def update_movement(self, dt, left, right):
        if left:
            if self.start_movement:
                self.vel = (-.001*dt, self.vel[1])
                self.acc = (0, self.acc[1])
            self.move_left(dt)
            self.start_movement = False
        elif right:
            if self.start_movement:
                self.vel = (.001*dt, self.vel[1])
                self.acc = (0, self.acc[1])
            self.move_right(dt)
            self.start_movement = False
        elif self.vel[0] > 0.0005*dt:
            self.acc = (-0.0001*dt, self.acc[1])
            self.start_movement = True
        elif self.vel[0] < -0.0005*dt:
            self.acc = (0.0001*dt, self.acc[1])
            self.start_movement = True
        else:
            self.vel = (0, self.vel[1])
            self.acc = (0, self.acc[1])
            self.start_movement = True

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

    def ai_random_move(self, dt):
        chance = random.random()
        left = False
        right = False
        if chance < 0.33:
            left = True
        elif chance < 0.66:
            right = True
        self.update_movement(dt, left, right)

    def is_dead(self, screen_height):
        return self.pos[1] > self.score_line + 0.66*screen_height + self.height

    def screen_wrap(self, screen_width):
        if self.pos[0] > screen_width:
            self.pos = (-self.width, self.pos[1])
        if self.pos[0] < -self.width:
            self.pos = (screen_width, self.pos[1])