import copy

import numpy as np
import pygame
from random import random
from vector import Vector


class Layer(object):
    def __init__(self, inputs: int, neurons: int, activation, weights, biases):
        self.neurons = neurons
        self.inputs = inputs
        self.weights = weights
        self.biases = biases
        self.activation = activation
        self.output = []

    @classmethod
    def random_layer(cls, inputs: int, neurons: int, activation):
        weights = np.random.standard_normal((inputs, neurons))
        biases = np.zeros((1, neurons))
        print(weights)

        return cls(inputs, neurons, activation, weights, biases)

    def forward(self, inputs):
        self.output = self.activation.forward(np.dot(inputs, self.weights) + self.biases)
        return self.output

    def get_neuron_state(self, neuron: int):
        return self.output[0][neuron]

    def copy(self):
        return Layer(self.inputs, self.neurons, self.activation, copy.deepcopy(self.weights),
                     copy.deepcopy(self.biases))

    def mutate(self, rate):
        def random_mutate(val, chance):
            if random() < chance:
                # chance to replace with random -1 to 1 number
                return random() * 2 - 1
            return val

        new_biases = []
        for bias in self.biases:
            new_biases.append(random_mutate(bias, rate))

        new_weights = []
        for neuron_weights in self.weights:
            new_neuron_weights = []
            for weight in neuron_weights:
                new_neuron_weights.append(random_mutate(weight, rate))
            new_weights.append(new_neuron_weights)

        self.weights = new_weights
        self.biases = new_biases


class InputLayer(Layer):
    def forward(self, inputs):
        self.output = [inputs]
        return self.output


class ReLU:
    def forward(self, inputs):
        return np.maximum(0, inputs)


class NeuralNetwork(object):
    def __init__(self, inputs: int, hidden_layers: int, hidden_nodes: int, outputs: int, activation):
        self.layers = []
        self.layers.append(InputLayer.random_layer(inputs, inputs, activation))
        self.layers.append(Layer.random_layer(inputs, hidden_nodes, activation))
        for x in range(1, hidden_layers):
            self.layers.append(Layer.random_layer(hidden_nodes, hidden_nodes, activation))
        self.layers.append(Layer.random_layer(hidden_nodes, outputs, activation))

    def add_layer(self, layer: Layer):
        self.layers.append(layer)

    def forward(self, inputs):
        for layer in self.layers:
            inputs = layer.forward(inputs)
        return inputs


class NetworkDisplay(object):
    def __init__(self, network: NeuralNetwork, position: Vector, dimensions: Vector, neuron_size: int):
        self.network = network
        self.position = position
        self.dimensions = dimensions
        self.neuron_size = neuron_size

        neuron_vertical_spacing = int(self.neuron_size * 4)

        self.neuron_positions = []
        # Neurons
        for i, layer in enumerate(self.network.layers):
            neuron_position_layer = []
            x = self.position.x + int(self.dimensions.x / len(self.network.layers) * i)
            y_offset = int((self.dimensions.y - layer.neurons * neuron_vertical_spacing) / 2)
            for neuron in range(0, layer.neurons):
                y = self.position.y + y_offset + neuron * neuron_vertical_spacing
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
                            colour = (100, -line_strength + 50, -line_strength + 50)
                        else:
                            colour = (line_strength + 50, line_strength + 50, 100)
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
