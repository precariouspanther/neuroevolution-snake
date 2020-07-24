import copy

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
        self.respawn()

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

    def respawn(self):
        self.snake = Snake(self, Vector(10 + randint(0, self.dimensions.x - 20), 5),
                           NeuralNetwork.create(10, 2, 20, 4, ReLU()))


class Snake(object):
    def __init__(self, grid: Grid, position: Vector, brain: NeuralNetwork):
        self.length = 1
        self.grid = grid
        self.position = position
        self.velocity = Vector(0, 0)
        self.tail = []
        self.alive = True
        self.brain = brain
        self.age = 0
        self.fitness = 0
        self.moves = 300
        self.food = Food(self.grid, self)

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
        self.moves -= 1

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
        if self.moves < 0:
            self.die()
            return

        self.position = new_position
        while len(self.tail) >= self.length:
            self.tail.pop(0)
        self.tail.append(new_position)

    def grow(self):
        self.length += 1
        self.moves += 100

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
        if self.length < 10:
            # Short snake. Focus on growth (without crashing)
            return self.age * pow(2, self.length)
        # Long snake. Emphasise staying alive with incremental growth
        return pow(self.age, 2) * pow(2, 10) * (self.length - 9)

    def senses(self):
        food_direction = self.position.sub(self.food.position)

        # Scan for collisions within 10 cells in each direction
        directions = [
            Vector(-1, 0),
            Vector(1, 0),
            Vector(0, -1),
            Vector(0, 1)
        ]

        for i, direction in enumerate(directions):
            ray = self.position.copy()
            for x in range(0, 10):
                ray = ray.add(direction)
                if self.is_collision(ray):
                    # Collision found. Record it
                    directions[i] = self.position.sub(ray)
                    break
                elif x is 9:
                    # No collision within 10 cells. Mark safe
                    directions[i] = Vector(10, 10)
        return [
            food_direction.x / self.grid.dimensions.x,
            food_direction.y / self.grid.dimensions.y,
            self.velocity.x,
            self.velocity.y,
            self.position.x / self.grid.dimensions.x,
            self.position.y / self.grid.dimensions.y,
            directions[0].x / 10,
            directions[1].x / 10,
            directions[2].y / 10,
            directions[3].y / 10,
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

