import sys
sys.path.append("src/ga")

from crossover import *
from mutation import *
from evolution import *

import pandas as pd

def run_ga(initial_population, objective_function, evolution_mechanism, end_condition, log_file="/home/nathan/Documents/GitHub/Bio-Inspired-Foot-Design/results/csv/ga_results.csv"):
    population = initial_population

    generation = 0
    data_df = pd.DataFrame({
        'generation':[],
        'num_pad_units':[],
        'pad_strength':[],
        'result':[],
    })


    while not end_condition():
        print("===================\ngeneration: ", population)

        population_results = objective_function(population)

        print("results: ", population_results)

        scenario_list = map(objective_function.binary_to_scenario, population)

        data_list = [
            {
                'generation': int(generation),
                'num_pad_units': scenario['claw_scenario']['num_pad_units'],
                'pad_strength': scenario['claw_scenario']['pad_strength'][0],
                'result': population_results[index],
            }
            for index, scenario in enumerate(scenario_list)
        ]

        # data_df = data_df.append(data_list)
        data_df = pd.concat([data_df, pd.DataFrame(data_list)], ignore_index=True)


        data_df.to_csv(log_file)
        
        population = evolution_mechanism(population, list(population_results))

        generation += 1


