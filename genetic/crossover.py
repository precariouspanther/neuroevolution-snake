from random import random

import numpy as np


# Simulated binary crossover https://engineering.purdue.edu/~sudhoff/ee630/Lecture04.pdf
# https://pdfs.semanticscholar.org/b8ee/6b68520ae0291075cb1408046a7dff9dd9ad.pdf
def SBC(mother: np.ndarray, father: np.ndarray, distribution_index):
    randoms = np.random.random(mother.shape)
    betas = np.empty(mother.shape)
    betas[randoms <= 0.5] = 2 * randoms[randoms <= 0.5]
    betas[randoms > 0.5] = 1.0 / (2.0 * (1.0 - randoms[randoms > 0.5]))
    betas **= 1.0 / (distribution_index + 1)

    child1 = 0.5 * ((1 + betas) * mother + (1 - betas) * father)
    child2 = 0.5 * ((1 - betas) * mother + (1 + betas) * father)
    return child1, child2

