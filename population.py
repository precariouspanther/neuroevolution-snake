from random import randint, random

import pygame

from neuralnetwork import NeuralNetwork, ReLU
from snake import Snake, Grid
from vector import Vector


class Population(object):
    def __init__(self, snake_count: int, grid_size: Vector, cell_size: int, position: Vector):
        self.best_score = 0
        self.snake_count = snake_count
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.position = position
        self.generations = 1
        self.grid = Grid(grid_size, position, cell_size)
        self.snakes = [Snake(self.grid, Vector(10 + randint(0, self.grid.dimensions.x - 20), 5),
                             NeuralNetwork.create(10, 2, 20, 4, ReLU())) for x in range(0, snake_count)]
        self.active_snake = self.snakes[0]

    def draw(self, game: pygame, display):

        self.grid.draw(pygame, display)

        for snake in self.snakes:
            snake.move()

            if not self.active_snake.alive:
                self.active_snake = snake
            if snake is not self.active_snake:
                snake.draw(pygame, display, snake is self.active_snake)

        if self.live_snakes() is 0:
            # all sneks ded. :'(
            self.next_generation()
        # Draw the first snake
        self.active_snake.draw(game, display, True)

    def live_snakes(self):
        alive = 0
        for snake in self.snakes:
            if snake.alive:
                alive += 1
        return alive

    def respawn(self):
        self.snakes = [Snake(self.grid, Vector(10 + randint(0, self.grid.dimensions.x - 20), 5),
                             NeuralNetwork.create(10, 2, 20, 4, ReLU())) for x in range(0, self.snake_count)]

    def next_generation(self):
        snakes = self.snakes
        snakes.sort(key=lambda snake: snake.fitness, reverse=True)

        best_snake = snakes[0]
        if best_snake.fitness > self.best_score:
            self.best_score = best_snake.fitness

        # normalise fitness scores
        top_fitness = best_snake.fitness
        total_fitness = 0
        for snake in snakes:
            snake.fitness /= top_fitness
            total_fitness += snake.fitness



        # Todo: clean up the violations of encapsulation here

        # New snake
        self.snakes = [Snake(self.grid, Vector(10 + randint(0, self.grid.dimensions.x - 20), 5), best_snake.brain)]

        # Baby snakes!
        for i in range(0, self.snake_count - 1):
            mother = self.select_parent(total_fitness, snakes)
            father = self.select_parent(total_fitness, snakes)
            child_brain = mother.brain.crossover(father.brain)
            child_brain.mutate(0.05)
            self.snakes.append(Snake(self.grid, Vector(10 + randint(0, self.grid.dimensions.x - 20), 5), child_brain))

        self.generations += 1

    def select_parent(self, total_fitness, snakes):
        rand_fitness = random() * total_fitness
        sum = 0
        for snake in snakes:
            sum += snake.fitness
            if sum > rand_fitness:
                return snake
        return snakes[0]