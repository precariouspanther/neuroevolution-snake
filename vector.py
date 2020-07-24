from math import sqrt


class Vector(object):
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def equals(self, compare):
        if compare.x is self.x and compare.y is self.y:
            return True
        return False

    def sub(self, vector):
        return Vector(self.x - vector.x, self.y - vector.y)

    def add(self, vector):
        return Vector(self.x + vector.x, self.y + vector.y)

    def copy(self):
        return Vector(self.x, self.y)

    def dist(self, vector):
        dist = pow(vector.x - self.x, 2) + pow(vector.x - self.x, 2)
        return sqrt(dist)

    def __repr__(self):
        return str(self.x) + " - " + str(self.y)
