import time

from random import randint, random

from neuralnetwork import NeuralNetwork, ReLU
from vector import Vector


# The grid a single snake lives on
class Grid(object):
    def __init__(self, dimensions: Vector, position: Vector, cell_size=10):
        self.dimensions = dimensions
        self.cell_size = cell_size
        self.position = position


class Snake(object):
    def __init__(self, grid: Grid, position: Vector, brain: NeuralNetwork, length=1):
        self.length = max(1, length)
        self.grid = grid
        self.position = position
        self.velocity = Vector(0, 1)
        self.tail = []
        self.alive = True
        self.brain = brain
        self.age = 0
        self.start_time = time.time()
        self.hunger = 200
        self.fitness = 0
        self.food = Food(self.grid, self)
        self.total_food_distance = 0

    def think(self):
        ideas = self.brain.forward(self.senses())[0]
        strongest_idea = 0
        strongest_index = None
        for i, idea in enumerate(ideas):
            if idea > strongest_idea:
                strongest_idea = idea
                strongest_index = i

        if strongest_index is 0:
            self.up()
        elif strongest_index is 1:
            self.down()
        elif strongest_index is 2:
            self.left()
        elif strongest_index is 3:
            self.right()

    def eat(self):
        self.grow()
        self.hunger += 100
        self.hunger = min(self.hunger, 500)
        last_food = self.food.position.copy()
        self.food.move()
        if self.length > 2:
            # we have travelled far, between foods. Keep track for fitness!
            self.total_food_distance += last_food.dist(self.food.position)

    def move(self):
        if not self.alive:
            return
        self.age += 1
        self.hunger -= 1

        if self.position.equals(self.food.position):
            # Nom.
            self.eat()

        self.think()

        new_position = self.position.add(self.velocity)

        # Collision
        if self.is_collision(new_position):
            self.die()
            return
        # Died of hunger...
        if self.hunger < 0:
            self.die()
            return

        self.position = new_position
        while len(self.tail) >= self.length:
            self.tail.pop(0)
        self.tail.append(new_position)

    def grow(self):
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
        # Alternative FF inspired by https://www.youtube.com/watch?v=vhiO4WsHA6c
        fitness = self.age + (pow(2, self.length) + pow(self.length, 2.1) * 500)
        fitness -= pow(self.length, 1.2) * pow(0.25 * self.age, 1.3)
        return fitness

    def senses(self):
        # Scan for collisions within 50 cells in each direction
        directions = [
            Vector(-1, 0),
            Vector(-1, -1),
            Vector(1, 0),
            Vector(1, -1),
            Vector(0, -1),
            Vector(1, 1),
            Vector(0, 1),
            Vector(-1, 1)
        ]
        food_vision = [0 for x in range(0, len(directions))]
        wall_vision = [0 for x in range(0, len(directions))]
        self_vision = [0 for x in range(0, len(directions))]

        for i, direction in enumerate(directions):
            ray = self.position.copy()
            for x in range(0, self.grid.dimensions.x):
                ray = ray.add(direction)

                # Wall!
                if ray.x < 0 or ray.y < 0 or ray.x > self.grid.dimensions.x - 1 or ray.y > self.grid.dimensions.y - 1:
                    wall_vision[i] = 1
                    break
                # Food!
                if ray.equals(self.food.position):
                    food_vision[i] = 1
                    break
                # Self...
                if self.is_collision(ray):
                    self_vision[i] = 1
                    break

        senses = []
        for vision in [food_vision, wall_vision, self_vision]:
            for direction in vision:
                senses.append(direction)

        senses.append(int(-self.velocity.y > 0))
        senses.append(int(self.velocity.y > 0))
        senses.append(int(-self.velocity.x > 0))
        senses.append(int(self.velocity.x > 0))

        return senses

    def is_collision(self, position: Vector):
        for segment in self.tail:
            if segment.equals(position):
                return True
        if position.x < 0 or position.y < 0:
            return True
        if position.x > self.grid.dimensions.x - 1 or position.y > self.grid.dimensions.y - 1:
            return True
        return False


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
