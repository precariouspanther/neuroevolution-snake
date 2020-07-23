import pygame
from random import randint

from neuralnetwork import NeuralNetwork, ReLU
from vector import Vector


# The grid a single snake lives on
class Grid(object):
    def __init__(self, dimensions: Vector, position: Vector, cell_size=10):
        self.dimensions = dimensions
        self.cell_size = cell_size
        self.position = position
        self.snake = None
        self.respawn()
        self.food = Food(self)

    def evaluate(self):
        # Snake
        self.snake.move()

        if self.snake.position.equals(self.food.position):
            # Nom.
            self.snake.grow()
            self.food.move()

    def draw(self, game: pygame, display):
        total_width = (self.cell_size + 2) * self.dimensions.x
        total_height = (self.cell_size + 2) * self.dimensions.y
        pygame.draw.rect(display, (255, 0, 255),
                         [self.position.x - 2, self.position.y - 2, total_width + 4, total_height + 4])
        pygame.draw.rect(display, (80, 80, 80), [self.position.x, self.position.y, total_width, total_height])

        snake_colour = (0, 255, 255)
        if not self.snake.alive:
            snake_colour = (255, 0, 0)
        for segment in self.snake.tail:
            pygame.draw.rect(display, snake_colour, self.cell_to_rect(segment))
        # Food
        pygame.draw.rect(display, (255, 0, 255), self.cell_to_rect(self.food.position))

    def cell_to_rect(self, position: Vector):
        return [
            self.position.x + (position.x * (self.cell_size + 2)) + 1,
            self.position.y + (position.y * (self.cell_size + 2)) + 1,
            self.cell_size,
            self.cell_size
        ]

    # Check if a position is already occupied or should be treated as a collision
    def is_collision(self, position: Vector):
        for segment in self.snake.tail:
            if segment.equals(position):
                return True
        if position.x < 0 or position.y < 0:
            return True
        if position.x > self.dimensions.x - 1 or position.y > self.dimensions.y - 1:
            return True
        return False

    def respawn(self):
        self.snake = Snake(self, Vector(10 + randint(0, self.dimensions.x - 20), 5),
                           NeuralNetwork.create(6, 2, 16, 4, ReLU()))


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
        self.moves = 200

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

        self.think()

        new_position = self.position.add(self.velocity)

        # Collision
        if self.grid.is_collision(new_position):
            self.die()
            return
        # Died of boredom...
        if self.moves is 0:
            self.die()
            return

        self.position = new_position
        while len(self.tail) >= self.length:
            self.tail.pop(0)
        self.tail.append(new_position)

    def grow(self):
        self.moves += 100
        self.length += 1

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
        return self.age + self.length * 10

    def senses(self):
        food_direction = self.position.sub(self.grid.food.position)

        return [
            food_direction.x / self.grid.dimensions.x,
            food_direction.y / self.grid.dimensions.y,
            self.velocity.x,
            self.velocity.y,
            self.position.x / self.grid.dimensions.x,
            self.position.y / self.grid.dimensions.y
        ]


class Food(object):
    def __init__(self, grid: Grid):
        self.grid = grid
        self.move()
        self.position = Vector(randint(1, self.grid.dimensions.x - 1), randint(1, self.grid.dimensions.y - 1))

    def move(self):
        while True:
            self.position = Vector(randint(1, self.grid.dimensions.x - 1), randint(1, self.grid.dimensions.y - 1))
            if not self.grid.is_collision(self.position):
                return


class Population(object):
    def __init__(self, snake_count: int, grid_size: Vector, cell_size: int, position: Vector):
        self.snake_count = snake_count
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.position = position
        self.generations = 1
        self.snake_grids = [Grid(grid_size, position, cell_size) for x in range(0, snake_count)]
        self.active_snake = self.snake_grids[0]

    def draw(self, game: pygame, display):

        for grid in self.snake_grids:
            grid.evaluate()
            if not self.active_snake.snake.alive:
                self.active_snake = grid

        if self.live_snakes() is 0:
            # all sneks ded. :'(
            self.next_generation()
        # Draw the first snake (all the others are just evaluated behind the scenes
        self.active_snake.draw(game, display)

    def live_snakes(self):
        alive = 0
        for grid in self.snake_grids:
            if grid.snake.alive:
                alive += 1
        return alive

    def respawn(self):
        self.snake_grids = [Grid(self.grid_size, self.position, self.cell_size) for x in range(0, self.snake_count)]
        pass

    def next_generation(self):
        snakes = [grid.snake for grid in self.snake_grids]
        snakes.sort(key=lambda snake: snake.fitness, reverse=True)

        best_snake = snakes[0]

        # Todo: clean up the violations of encapsulation here

        # New grids
        self.snake_grids = [Grid(self.grid_size, self.position, self.cell_size) for x in range(0, self.snake_count)]

        # Some brain surgery... Clone our best snake and transplant its brain into all the newly labotomised snakes
        for i, grid in enumerate(self.snake_grids):
            grid.snake.brain = best_snake.brain.copy()
            grid.snake.brain.mutate(0.05)

        self.generations += 1
