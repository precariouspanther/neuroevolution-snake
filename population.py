import time
from copy import deepcopy
from random import randint, random

import pygame

from neuralnetwork import NeuralNetwork, ReLU
from snake import Snake, Grid
from vector import Vector


class Population(object):
    def __init__(self, snake_count: int, grid_size: Vector, cell_size: int, position: Vector):
        self.start_time = time.time()
        self.duration = 0
        self.best_length = 0
        self.best_score = 0
        self.snake_count = snake_count
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.position = position
        self.generations = 1
        self.grid = Grid(grid_size, position, cell_size)
        self.snakes = [Snake(self.grid, Vector(10 + randint(0, self.grid.dimensions.x - 20),
                                               10 + randint(0, self.grid.dimensions.y - 20)),
                             NeuralNetwork.create(10, 2, 24, 4, ReLU())) for x in range(0, snake_count)]
        self.active_snake = self.snakes[0]
        self.all_time_best_snake = self.active_snake
        self.history = []

        def noop():
            pass

        self.on_generation = noop

    def draw(self, game: pygame, display):
        self.grid.draw(game, display)
        for snake in self.snakes:
            if snake is not self.active_snake:
                snake.draw(game, display, False)

        self.active_snake.draw(game, display, True)

    def move(self):
        for snake in self.snakes:
            snake.move()

            if snake.length > self.best_length:
                self.best_length = snake.length

            if not self.active_snake.alive:
                max_len = 0
                for snake2 in self.snakes:
                    if snake2.length > max_len and snake2.alive:
                        max_len = snake2.length
                        self.active_snake = snake2

        if self.live_snakes() is 0:
            # all sneks ded. :'(
            self.next_generation()

    def live_snakes(self):
        alive = 0
        for snake in self.snakes:
            if snake.alive:
                alive += 1
        return alive

    def next_generation(self):
        snakes = self.snakes
        snakes.sort(key=lambda snake: snake.fitness, reverse=True)

        best_snake = snakes[0]
        if best_snake.fitness > self.best_score:
            self.best_score = best_snake.fitness
            self.all_time_best_snake = deepcopy(best_snake)

        # Discard worst snakes
        snakes = snakes[0:200]

        # normalise fitness scores
        top_fitness = best_snake.fitness
        top_length = 0
        total_fitness = 0
        for snake in snakes:
            top_length = max(snake.length, top_length)
            snake.fitness /= top_fitness
            total_fitness += snake.fitness

        self.history.append(
            {"score": top_fitness, "length": top_length, "duration": int(time.time() - self.start_time)})

        # Reset timer
        self.start_time = time.time()

        # Next generation snakes. A clone of the best from the last generation and all time
        # best are always included
        self.snakes = [
            Snake(self.grid, Vector(10 + randint(0, self.grid.dimensions.x - 20), 5), best_snake.brain),
            Snake(self.grid, Vector(10 + randint(0, self.grid.dimensions.x - 20), 5), self.all_time_best_snake.brain)
        ]

        # Baby snakes!
        for i in range(0, self.snake_count - 2):
            mother = self.select_parent(total_fitness, snakes)
            father = self.select_parent(total_fitness, snakes)
            child_brain = mother.brain.crossover(father.brain)
            child_brain.mutate(0.05)
            self.snakes.append(Snake(self.grid, Vector(10 + randint(0, self.grid.dimensions.x - 20),
                                                       10 + randint(0, self.grid.dimensions.y - 20)), child_brain))

        self.generations += 1
        self.active_snake = self.snakes[0]
        self.on_generation()

    def select_parent(self, total_fitness, snakes):
        rand_fitness = random() * total_fitness
        if random() > 0.5:
            # Additional bias towards stronger parents
            rand_fitness /= 2
        sum = 0
        for snake in snakes:
            sum += snake.fitness
            if sum > rand_fitness:
                return snake
        return snakes[0]

    def save_data(self):
        return (
            self.snakes, self.history, self.best_length, self.best_score, self.generations, self.all_time_best_snake,
            self.active_snake)

    def load_data(self, data):
        self.snakes = data[0]
        self.history = data[1]
        self.best_length = data[2]
        self.best_score = data[3]
        self.generations = data[4]
        self.all_time_best_snake = data[5]
        self.active_snake = data[6]
