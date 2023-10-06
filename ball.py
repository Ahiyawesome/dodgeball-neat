import pygame as pg


class Ball:
    def __init__(self, x, y, width, height, speed, tag):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.tag = tag

    def move(self):
        self.x += self.speed

    def draw(self, win):
        pg.draw.rect(win, self.tag, pg.Rect(self.x, self.y, self.width, self.height))
