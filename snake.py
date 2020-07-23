import pygame
from random import randint
from vector import Vector


# The grid a single snake lives on
class Grid(object):
    def __init__(self, dimensions: Vector, position: Vector, cell_size=10):
        self.dimensions = dimensions
        self.cell_size = cell_size
        self.position = position
        self.snake = Snake(self, 1, 5, 5)
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
        self.snake = Snake(self, 1, 10 + randint(0, self.dimensions.x - 20), 5)


class Snake(object):
    def __init__(self, grid: Grid, length=1, x=1, y=1):
        self.length = length
        self.grid = grid
        self.position = Vector(x, y)
        self.velocity = Vector(0, 1)
        self.tail = []
        self.alive = True

    def move(self):
        if not self.alive:
            return

        new_position = self.position.add(self.velocity)

        # Collision
        if self.grid.is_collision(new_position):
            self.alive = False
            return

        self.position = new_position
        while len(self.tail) >= self.length:
            self.tail.pop(0)
        self.tail.append(new_position)

    def grow(self):
        self.length += 1

    def shrink(self):
        self.length -= 1
        if self.length < 1:
            self.length = 1

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

    def fitness(self):
        return self.length * 10

    def get_senses(self):
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
        self.snake_grids = [Grid(grid_size, position, cell_size) for x in range(0, snake_count)]

    def draw(self, game: pygame, display):
        for grid in self.snake_grids:
            grid.evaluate()

        # Draw the first snake (all the others are just evaluated as is.
        self.snake_grids[0].draw(game, display)
