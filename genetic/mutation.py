import numpy as np


# Gaussian mutation. https://github.com/Chrispresso/SnakeAI/blob/master/genetic_algorithm/mutation.py
def gaussian(chromosome: np.ndarray, chance=0, scale=0):
    genes_to_mutate = np.random.random(chromosome.shape) < chance
    mutation = np.random.normal(size=chromosome.shape)
    mutation[genes_to_mutate] *= scale

    chromosome[genes_to_mutate] += mutation[genes_to_mutate]

    return chromosome
