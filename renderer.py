import pygame

from population import Population
from snake import Snake, Grid
from vector import Vector


class Renderer(object):
    def __init__(self, game: pygame, display, population: Population, cell_size: int, position: Vector):
        self.game = game
        self.display = display
        self.cell_size = cell_size
        self.position = position
        self.population = population

    def draw(self):
        self.draw_grid(self.population.grid)

        for snake in self.population.snakes:
            if snake is not self.population.active_snake:
                self.draw_snake(snake, False)

        self.draw_snake(self.population.active_snake, True)

    def draw_snake(self, snake: Snake, focus: bool):
        snake_colour = (0, 255, 255)
        food_colour = (255, 0, 255)
        if not focus:
            snake_colour = (0, 120, 120)
            food_colour = (120, 0, 120)
        if not snake.alive:
            return
        for segment in snake.tail:
            pygame.draw.rect(self.display, snake_colour, self.cell_to_rect(segment))
        # Food
        pygame.draw.rect(self.display, food_colour, self.cell_to_rect(snake.food.position))

    def draw_grid(self, grid: Grid):
        total_width = (self.cell_size + 2) * grid.dimensions.x
        total_height = (self.cell_size + 2) * grid.dimensions.y
        pygame.draw.rect(self.display, (255, 0, 255),
                         [self.position.x - 2, self.position.y - 2, total_width + 4, total_height + 4])
        pygame.draw.rect(self.display, (80, 80, 80), [self.position.x, self.position.y, total_width, total_height])

    def cell_to_rect(self, position: Vector):
        return [
            self.position.x + (position.x * (self.cell_size + 2)) + 1,
            self.position.y + (position.y * (self.cell_size + 2)) + 1,
            self.cell_size,
            self.cell_size
        ]
