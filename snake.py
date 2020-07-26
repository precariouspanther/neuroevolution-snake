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
        self.hunger = 10  # will starve in 10 seconds if we don't eat!
        self.fitness = 0
        self.food = Food(self.grid, self)

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

    def move(self):
        if not self.alive:
            return
        self.age += 1

        if self.position.equals(self.food.position):
            # Nom.
            self.grow()
            self.hunger += 5
            self.food.move()

        self.think()

        new_position = self.position.add(self.velocity)

        # Collision
        if self.is_collision(new_position):
            self.die()
            return
        # Died of hunger...
        if time.time() - self.start_time > self.hunger:
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
        # Age in seconds. The longer you live, the better your fitness
        age_in_seconds = int(time.time() - self.start_time)
        fitness = age_in_seconds

        if self.length > 3:
            # After reaching at least a length of 3, bonus fitness for speed in collecting food.
            fitness += int(self.length / age_in_seconds) * 2

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

        food_vector = self.food.position.sub(self.position)
        dist_above = max(0, -food_vector.y)  # 50
        dist_below = max(0, food_vector.y)  # 0
        dist_left = max(0, -food_vector.x)  # 0
        dist_right = max(0, food_vector.x)  # 20

        max_dist = max(dist_below, dist_above, dist_right, dist_left)

        return [
            dist_above / max_dist,
            dist_below / max_dist,
            dist_left / max_dist,
            dist_right / max_dist,
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
