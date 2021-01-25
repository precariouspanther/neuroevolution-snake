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


def SPBC(mother: np.ndarray, father: np.ndarray):
    child1 = mother.copy()
    child2 = father.copy()

    row_cut = np.random.randint(0, mother.shape[0])
    col_cut = np.random.randint(0, mother.shape[1]) +1

    child1[:row_cut, :] = father[:row_cut, :]
    child2[:row_cut, :] = mother[:row_cut, :]

    child1[row_cut, :col_cut] = father[row_cut, :col_cut]
    child2[row_cut, :col_cut] = mother[row_cut, :col_cut]

    return child1, child2


def random_crossover(mother: np.ndarray, father: np.ndarray, distribution_index):
    if random() > 0.5:
        return SBC(mother, father, distribution_index)
    return SPBC(mother, father)
