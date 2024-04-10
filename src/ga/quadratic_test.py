from typing import Any
import numpy as np
from utilities import map_range

from ga import run_ga

from crossover import *
from mutation import *
from evolution import *
from end_condition import *

def initialize_population(population_size, population_range):
    initial_population = np.uint8(map_range(np.random.rand(population_size), *population_range))

    return initial_population


class QuadraticObjective:
    def __init__(self, left_pole, right_pole) -> None:
        self.left_pole = left_pole
        self.right_pole = right_pole

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.evaluate_population(*args, **kwds)
    
    def evaluate_population(self, population):
        population_results = list(map(self.evaluate, population))
        return population_results

    def evaluate(self, x):
        return -(x - self.left_pole) * (x - self.right_pole)


if __name__ == '__main__':
    population_size = 150

    initial_population = initialize_population(
        population_size = population_size,
        population_range = (0,255),
    )

    objective_function = QuadraticObjective(
        left_pole = 0,
        right_pole = 256
    )

    crossover_mechanism = SimpleCrossover(
        crossover_point = 4
    )

    evolution_mechanism = LastNReplacement(
        n_replacement = 10,
        crossover_mechanism = crossover_mechanism
    )

    end_condition = MaxTrials(100)

    run_ga(
        initial_population = initial_population,
        objective_function = objective_function,
        evolution_mechanism = evolution_mechanism,
        end_condition = end_condition,
        )