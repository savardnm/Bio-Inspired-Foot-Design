import sys
sys.path.append("src/ga")

from crossover import *
from mutation import *
from evolution import *

def run_ga(initial_population, objective_function, evolution_mechanism, end_condition):
    population = initial_population


    while not end_condition():
        population_results = objective_function(population)

        print("==================>\n", population, population_results, "\n<=================")
        
        population = evolution_mechanism(population, list(population_results))


