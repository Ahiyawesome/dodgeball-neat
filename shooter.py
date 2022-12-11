import pygame as pg


class Shooter:
    def __init__(self, x, y, width, height, speed, color):
        self.x = self.orX = x
        self.y = self.orY = y
        self.width = width
        self.height = height
        self.speed = speed
        self.color = color
        self.shoot = False

    def draw(self, win):
        pg.draw.rect(win, self.color, pg.Rect(self.x, self.y, self.width, self.height))

    def what_to_do(self, state):
        if state == 0:                                # up
            self.y -= self.speed
        elif state == 1:                              # down
            self.y += self.speed
        elif state == 2:                              # shoot
            self.shoot = True

    def reset_position(self):
        self.x = self.orX
        self.y = self.orY