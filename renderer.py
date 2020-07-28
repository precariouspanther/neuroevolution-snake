import pygame

from neuralnetwork import NeuralNetwork
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
        if focus:
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


class NetworkDisplay(object):
    def __init__(self, network: NeuralNetwork, position: Vector, dimensions: Vector, neuron_size: int):
        self.network = network
        self.position = position
        self.dimensions = dimensions
        self.neuron_size = neuron_size
        padding = 20

        neuron_vertical_spacing = int(self.neuron_size * 4)

        self.neuron_positions = []

        width_per_layer = (self.dimensions.x - padding * 2) / len(self.network.layers)
        max_neurons = max(*[layer.neurons for layer in self.network.layers])
        height_per_neuron = (self.dimensions.y - padding * 2) / max_neurons

        # Neurons
        for i, layer in enumerate(self.network.layers):
            neuron_position_layer = []
            x = int(self.position.x + padding + width_per_layer * i)
            y_offset = ((max_neurons - layer.neurons) / 2) * height_per_neuron
            for neuron in range(0, layer.neurons):
                y = int(self.position.y + y_offset + neuron * height_per_neuron)
                neuron_position_layer.append(Vector(x, y))

            self.neuron_positions.append(neuron_position_layer)

    def draw(self, game: pygame, display):

        # Draw weights
        for i, layer in enumerate(self.neuron_positions):
            for neuron_index, neuron in enumerate(layer):
                if i is not 0:
                    for weight_offset, weight in enumerate(self.network.layers[i].weights.T[neuron_index]):
                        previous_layer = self.neuron_positions[i - 1]
                        previous_neuron = previous_layer[weight_offset]
                        line_strength = int(weight * 10)

                        if line_strength < 0:
                            colour = (100, min(255, -line_strength + 50), min(255, -line_strength + 50))
                        else:
                            colour = (min(255, line_strength + 50), min(255, line_strength + 50), 100)
                        pygame.draw.line(display, colour, [neuron.x, neuron.y],
                                         [previous_neuron.x, previous_neuron.y], 1)

        # Draw neurons
        for layer_index, layer in enumerate(self.neuron_positions):
            for neuron_index, neuron in enumerate(layer):
                pygame.draw.circle(display, (255, 255, 255), [neuron.x, neuron.y], self.neuron_size + 1)
                state = self.network.layers[layer_index].get_neuron_state(neuron_index)
                if state > 0:
                    brightness = min(255, int(state * 255))
                    pygame.draw.circle(display, (brightness, brightness, brightness), [neuron.x, neuron.y],
                                       self.neuron_size)
                else:
                    pygame.draw.circle(display, (40, 40, 40), [neuron.x, neuron.y], self.neuron_size)
