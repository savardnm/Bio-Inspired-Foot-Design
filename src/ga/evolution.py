from typing import Any
from mutation import *


class LastNReplacement:
    def __init__(
        self, n_replacement, crossover_mechanism, mutation_mechanism=NoMutation
    ) -> None:
        self.n_replacement = n_replacement
        self.crossover_mechanism = crossover_mechanism
        self.mutation_mechanism = mutation_mechanism

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.evolve_next_generation(*args, **kwargs)

    def evolve_next_generation(self, population, results):
        best_performers = self.extract_best_performers(
            population, results, len(population) - self.n_replacement
        )

        replacement_children = self.crossover_mechanism(
            parent_list=self.extract_best_performers(
                population, results, self.n_replacement, paired=True
            )
        )

        next_generation = best_performers + replacement_children

        # TODO Add mutation if necessary

        return next_generation

    def extract_best_performers(self, population, results, num, paired=False):
        population_results = list(zip(population, results))
        sorted_population = sorted(  # Sort based on result
            population_results, key=lambda x: x[1], reverse=True
        )

        best_performers = [x[0] for x in sorted_population[0:num]]

        if paired:
            return zip(best_performers[::2], best_performers[1::2])

        return best_performers
