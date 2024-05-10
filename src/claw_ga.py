from typing import Any
import numpy as np
from ga.utilities import map_range, extract_gene

from ga.ga import run_ga, population_from_csv
from pprint import pprint

from ga.crossover import *
from ga.mutation import *
from ga.evolution import *
from ga.end_condition import *

from coppelia_files.claws import *
from coppelia_files.scenes import *

import multiprocessing
from zmq_claw_test import batch_claw_test


def initialize_population(population_size, population_range):
    initial_population = np.uint32(map_range(np.random.rand(population_size), *population_range))

    return initial_population


class GripStrengthObjective:
    def __init__(self, max_processes=6) -> None:
        self.max_processes = max_processes

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.evaluate_population(*args, **kwds)

    def evaluate_population(self, binary_population):
        return batch_claw_test(map(self.binary_to_scenario, binary_population), self.max_processes)

    def binary_to_scenario(self, binary):
        # num_pad_units = int(binary & np.uint8(0b111))
        num_pad_units = int(extract_gene(binary, 0,3))
        
        # pad_strength = (binary & np.uint8(0b11111000)) >> 3
        pad_strength = extract_gene(binary, 3, 8)
        
        pad_strength = int(map_range(
            pad_strength,
            min_value = 5,
            max_value = 400,
            min_input = 0b0,
            max_input = 0b11111 
        ))
        
        pad_strength = (pad_strength, 10) # use 10 as default drag value

        pad_start_point_sign = extract_gene(binary, 8, 9)
        pad_start_point_value = extract_gene(binary, 9, 10)

        if pad_start_point_sign == 0:
            pad_start_point_sign = -1
        else:
            pad_start_point_sign = 1

        pad_start_pos = int(pad_start_point_sign * pad_start_point_value)


        scale = extract_gene(binary, 10, 18)
        scale = float(map_range(
            scale,
            min_value = 0.9,
            max_value = 1.1,
            min_input = 0x0,
            max_input = 0xff
        ))

        curvature = extract_gene(binary, 18, 26)

        curvature = float(map_range(
            curvature,
            min_value = -0.087, # +/- 5 degrees
            max_value = 0.087,
            min_input = 0x0,
            max_input = 0xff
        ))



        claw_scenario = {
            "path": Louse_Pad_Script_Extended,
            "num_pad_units": num_pad_units,
            "pad_strength": pad_strength,
            "pad_starting_pos": pad_start_pos,
            "curvature": curvature,
            "scale": scale
        }


        force_scenario = {
            "starting_value": 1.0,
            "mode": "hybrid",
            "lin_rate": 500.0,
            "exp_rate": 1.1,
        }

        scenario = {
            "scene": flex_pole_scene_5cm,
            "claw_scenario": claw_scenario,
            "actuator": {
                "name": "VerticalForce",
                "force": force_scenario,
                "wait_time": 1.0,
                "position_threshold": 0.1,
            },
            "headless": True,
            "autoquit": True,
        }

        return scenario


if __name__ == '__main__':
    population_size = 40
    gene_size=25

    initial_population = initialize_population(
        population_size = population_size,
        population_range = (0x0,0xffffffff),
    )

    # initial_population = population_from_csv("/home/nathan/Documents/GitHub/Bio-Inspired-Foot-Design/results/csv/ga_results_complex.csv")

    objective_function = GripStrengthObjective(
        max_processes=population_size
    )

    crossover_mechanism = SingleRandomCrossover(
        gene_size=gene_size
    )

    evolution_mechanism = LastNReplacement(
        n_replacement = 4,
        crossover_mechanism = crossover_mechanism,
        mutation_mechanism = RandomMutation(mutation_probability=0.03, gene_size=gene_size)
    )

    end_condition = MaxTrials(20)

    # batch_claw_test(scenario_list, max_processes=1)

    run_ga(
        initial_population = initial_population,
        objective_function = objective_function,
        evolution_mechanism = evolution_mechanism,
        end_condition = end_condition,
        log_file="/home/nathan/Documents/GitHub/Bio-Inspired-Foot-Design/results/csv/ga_results_complex.csv"
        )

    
