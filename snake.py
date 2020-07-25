import copy
import time

import pygame
from random import randint, random

from neuralnetwork import NeuralNetwork, ReLU
from vector import Vector


# The grid a single snake lives on
class Grid(object):
    def __init__(self, dimensions: Vector, position: Vector, cell_size=10):
        self.dimensions = dimensions
        self.cell_size = cell_size
        self.position = position

    def draw(self, game: pygame, display):
        total_width = (self.cell_size + 2) * self.dimensions.x
        total_height = (self.cell_size + 2) * self.dimensions.y
        pygame.draw.rect(display, (255, 0, 255),
                         [self.position.x - 2, self.position.y - 2, total_width + 4, total_height + 4])
        pygame.draw.rect(display, (80, 80, 80), [self.position.x, self.position.y, total_width, total_height])

    def cell_to_rect(self, position: Vector):
        return [
            self.position.x + (position.x * (self.cell_size + 2)) + 1,
            self.position.y + (position.y * (self.cell_size + 2)) + 1,
            self.cell_size,
            self.cell_size
        ]


class Snake(object):
    def __init__(self, grid: Grid, position: Vector, brain: NeuralNetwork, length=1):
        self.length = max(1, length)
        self.grid = grid
        self.position = position
        self.velocity = Vector(0, 0)
        self.tail = []
        self.alive = True
        self.brain = brain
        self.age = 0
        self.start_time = time.time()
        self.fitness = 0
        self.food = Food(self.grid, self)
        self.last_meal = time.time()

    def think(self):
        idea = self.brain.forward(self.senses())[0]
        if idea[0] > 0.7:
            self.up()
        elif idea[1] > 0.7:
            self.down()
        elif idea[2] > 0.7:
            self.left()
        elif idea[3] > 0.7:
            self.right()

    def move(self):
        if not self.alive:
            return
        self.age += 1

        if self.position.equals(self.food.position):
            # Nom.
            self.grow()
            self.food.move()

        self.think()

        new_position = self.position.add(self.velocity)

        # Collision
        if self.is_collision(new_position):
            self.die()
            return
        # Died of boredom...
        if time.time() - self.last_meal > 5:
            self.die()
            return

        self.position = new_position
        while len(self.tail) >= self.length:
            self.tail.pop(0)
        self.tail.append(new_position)

    def grow(self):
        self.length += 1
        self.last_meal = time.time()

    def die(self):
        self.fitness = self.calculate_fitness()
        self.alive = False

    def up(self):
        if self.velocity.y is 1:
            return
        self.velocity = Vector(0, -1)

    def down(self):
        if self.velocity.y is -1:
            return
        self.velocity = Vector(0, 1)

    def left(self):
        if self.velocity.x is 1:
            return
        self.velocity = Vector(-1, 0)

    def right(self):
        if self.velocity.x is -1:
            return
        self.velocity = Vector(1, 0)

    def calculate_fitness(self):
        # Age in seconds. The longer you live, the better your fitness
        age_in_seconds = int(time.time() - self.start_time)
        fitness = age_in_seconds

        if self.length > 5:
            # After reaching at least a length of 5, bonus fitness for speed in collecting food.
            fitness += int(self.length / age_in_seconds)

        return fitness

    def senses(self):
        # Scan for collisions within 50 cells in each direction
        directions = [
            Vector(-1, 0),
            Vector(1, 0),
            Vector(0, -1),
            Vector(0, 1)
        ]

        for i, direction in enumerate(directions):
            ray = self.position.copy()
            for x in range(0, 50):
                ray = ray.add(direction)
                if self.is_collision(ray):
                    # Collision found. Record it
                    if ray.x + ray.y > self.position.x + self.position.y:
                        directions[i] = ray.sub(self.position)
                    else:
                        directions[i] = self.position.sub(ray)
                    break
                elif x is 49:
                    # No collision within 10 cells. Mark safe
                    directions[i] = Vector(50, 50)
        return [
            self.food.position.y < self.position.y,
            self.food.position.y > self.position.y,
            self.food.position.x < self.position.x,
            self.food.position.x > self.position.x,
            self.velocity.x,
            self.velocity.y,
            1 - (directions[0].x / 50),
            1 - (directions[1].x / 50),
            1 - (directions[2].y / 50),
            1 - (directions[3].y / 50),
        ]

    def is_collision(self, position: Vector):
        for segment in self.tail:
            if segment.equals(position):
                return True
        if position.x < 0 or position.y < 0:
            return True
        if position.x > self.grid.dimensions.x - 1 or position.y > self.grid.dimensions.y - 1:
            return True
        return False

    def draw(self, game: pygame, display, focus: bool):
        snake_colour = (0, 255, 255)
        food_colour = (255, 0, 255)
        if not focus:
            snake_colour = (0, 120, 120)
            food_colour = (120, 0, 120)
        if not self.alive:
            return
        for segment in self.tail:
            pygame.draw.rect(display, snake_colour, self.grid.cell_to_rect(segment))
        # Food
        pygame.draw.rect(display, food_colour, self.grid.cell_to_rect(self.food.position))


class Food(object):
    def __init__(self, grid: Grid, snake: Snake):
        self.grid = grid
        self.snake = snake
        self.move()
        self.position = Vector(randint(1, self.grid.dimensions.x - 1), randint(1, self.grid.dimensions.y - 1))

    def move(self):
        while True:
            self.position = Vector(randint(1, self.grid.dimensions.x - 1), randint(1, self.grid.dimensions.y - 1))
            if not self.snake.is_collision(self.position):
                return
