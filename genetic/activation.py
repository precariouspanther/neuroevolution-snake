import numpy as np


class ReLU:
    def forward(self, inputs):
        return np.maximum(0, inputs)


class Sigmoid:
    def forward(self, inputs):
        return 1.0 / (1.0 + np.exp(-inputs))
