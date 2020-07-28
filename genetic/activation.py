import numpy as np
from scipy.special import expit


class ReLU:
    def forward(self, inputs):
        return np.maximum(0, inputs)


class Sigmoid:
    def forward(self, inputs):
        return expit(inputs)
