import sys
sys.path.append("src/ga")

from crossover import *
from mutation import *
from evolution import *

import pandas as pd

def run_ga(initial_population, objective_function, evolution_mechanism, end_condition, log_file):
    population = initial_population

    generation = 0
    data_df = pd.DataFrame({
        'generation':[],
        'num_pad_units':[],
        'pad_strength':[],
        "pad_starting_pos":[],
        "curvature":[],
        "scale":[],
        'result':[],
        'binary':[],
    })


    while not end_condition():
        print("===================\ngeneration: ", population)

        population_results1, population_results2 = objective_function(population)

        print("results: ", population_results1, population_results2)

        scenario_list = map(objective_function.binary_to_scenario, population)

        data_list = [
            {
                'generation': int(generation),
                'num_pad_units': scenario['claw_scenario']['num_pad_units'],
                'pad_strength': scenario['claw_scenario']['pad_strength'][0],
                'pad_starting_pos':scenario['claw_scenario']['pad_starting_pos'],
                'curvature':scenario['claw_scenario']['curvature'],
                'scale':scenario['claw_scenario']['scale'],
                'vertical_result': population_results1[index],
                'horizontal_result': population_results2[index],
                'result': (population_results1[index] * population_results2[index]),
                'binary': population[index],
            }
            for index, scenario in enumerate(scenario_list)
        ]

        # data_df = data_df.append(data_list)
        data_df = pd.concat([data_df, pd.DataFrame(data_list)], ignore_index=True)


        data_df.to_csv(log_file)
        
        population = evolution_mechanism(population, [scenario['result'] for scenario in data_list])

        generation += 1



def population_from_csv(csv_file):
    df = pd.read_csv(csv_file)
    last_generation = max(df["generation"].unique())
    last_generation_df = df[df["generation"].isin([last_generation])]
    population = list(np.uint32(list(last_generation_df['binary'])))
    return population