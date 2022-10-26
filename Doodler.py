# Project: DoodleJump-NEAT-AI
# Authors: Alex Miller and Ruihang Liu
# Email: alexjmil@bu.edu and hrl@bu.edu
# File description (Doodler.py): creates a 
# class for the player of the game

class Doodler:
    def __init__():
        self.img = pg.image.load("Doodler.jpg").convert()
        self.rect = img.get_rect()
        self.pos = (WIDTH / 2, HEIGHT - 100)
        self.vel = (0, 0)
        self.acc = (0, 0)

    def display(surf):
        surf.blit(self.img, self.pos)

    def move():
        self.pos = tuple(sum(x) for x in zip(self.pos, self.vel))
        self.vel = tuple(sum(x) for x in zip(self.vel, self.acc))