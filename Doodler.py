# Project: DoodleJump-NEAT-AI
# Authors: Alex Miller and Ruihang Liu
# Email: alexjmil@bu.edu and hrl@bu.edu
# File description (Doodler.py): creates a 
# class for the player of the game
import pygame as pg

class Doodler:
    def __init__(self, WIDTH, HEIGHT):
        self.img = pg.image.load("doodler.png").convert()
        self.rect = self.img.get_rect()
        self.prev_pos = (WIDTH / 2, HEIGHT - 100)
        self.pos = (WIDTH / 2, HEIGHT - 100)
        self.vel = (0, 0)
        self.acc = (0, 0)
        self.score = 0

    def display(self, surf):
        surf.blit(self.img, self.pos)

    def move(self):
        self.prev_pos = self.pos
        self.pos = tuple(sum(x) for x in zip(self.pos, self.vel))
        self.vel = tuple(sum(x) for x in zip(self.vel, self.acc))