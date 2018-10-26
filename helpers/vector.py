#! /usr/bin/python3

from math import sqrt


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def length(self):
        return int(sqrt(self.x ** 2 + self.y ** 2))

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __str__(self):
        return "[x: {}, y: {}]".format(self.x, self.y)