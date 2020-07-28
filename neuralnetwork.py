import copy

import numpy as np
import pygame

from genetic.activation import Sigmoid
from genetic.crossover import SBC
from genetic.mutation import gaussian
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

        return cls(inputs, neurons, activation, weights, biases)

    def forward(self, inputs):
        self.output = self.activation.forward(np.dot(inputs, self.weights) + self.biases)
        return self.output

    def get_neuron_state(self, neuron: int):
        return self.output[0][neuron]

    def copy(self):
        return Layer(self.inputs, self.neurons, self.activation, copy.deepcopy(self.weights),
                     copy.deepcopy(self.biases))

    def mutate(self, rate, scale):
        self.biases = gaussian(self.biases, rate, scale)
        self.biases.clip(-1, 1, self.biases)
        self.weights = gaussian(self.weights, rate, scale)
        self.weights.clip(-1, 1, self.weights)

    def crossover(self, father):
        # Crossover using simulated binary crossover
        c1_weights, c2_weights = SBC(self.weights, father.weights, 5)
        c1_biases, c2_biases = SBC(self.biases, father.biases, 5)

        c1 = Layer(self.inputs, self.neurons, self.activation, c1_weights, c1_biases)
        c2 = Layer(self.inputs, self.neurons, self.activation, c2_weights, c2_biases)

        return c1, c2


class InputLayer(Layer):
    def forward(self, inputs):
        self.output = [inputs]
        return self.output


class NeuralNetwork(object):
    def __init__(self, layers):
        self.layers = layers

    @classmethod
    def create(cls, inputs: int, hidden_layers: list, outputs: int, activation):
        layers = [InputLayer.random_layer(inputs, inputs, activation)]
        next_inputs = inputs
        for layer_neurons in hidden_layers:
            layers.append(Layer.random_layer(next_inputs, layer_neurons, activation))
            next_inputs = layer_neurons
        layers.append(Layer.random_layer(next_inputs, outputs, Sigmoid()))
        return cls(layers)

    def add_layer(self, layer: Layer):
        self.layers.append(layer)

    def forward(self, inputs):
        for layer in self.layers:
            inputs = layer.forward(inputs)
        return inputs

    def mutate(self, rate, scale):
        for layer in self.layers:
            layer.mutate(rate, scale)

    def copy(self):
        return NeuralNetwork(copy.deepcopy(self.layers))

    def crossover(self, father):
        c1_layers = []
        c2_layers = []

        for mother_layer, father_layer in zip(self.layers, father.layers):
            c1_layer, c2_layer = mother_layer.crossover(father_layer)
            c1_layers.append(c1_layer)
            c2_layers.append(c2_layer)

        return NeuralNetwork(c1_layers), NeuralNetwork(c2_layers)
