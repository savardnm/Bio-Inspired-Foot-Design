from typing import Any
import numpy as np
from ga.utilities import map_range

from ga.ga import run_ga
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
    initial_population = np.uint8(map_range(np.random.rand(population_size), *population_range))

    return initial_population


class GripStrengthObjective:
    def __init__(self, max_processes=6) -> None:
        self.max_processes = max_processes

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.evaluate_population(*args, **kwds)

    def evaluate_population(self, binary_population):
        return batch_claw_test(map(self.binary_to_scenario, binary_population), self.max_processes)

    def binary_to_scenario(self, binary):
        num_pad_units = int(binary & np.uint8(0b111))
        
        pad_strength = (binary & np.uint8(0b11111000)) >> 3
        
        pad_strength = int(map_range(
            pad_strength,
            min_value = 5,
            max_value = 400,
            min_input = 0b0,
            max_input = 0b11111 
        ))

        pad_strength = (pad_strength, 10) # use 10 as default drag value

        claw_scenario = {
            "path": Louse_Pad_Script,
            "num_pad_units": num_pad_units,
            "pad_strength": pad_strength,
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
            "headless": False,
            "autoquit": True,
        }

        return scenario


if __name__ == '__main__':
    population_size = 10

    initial_population = initialize_population(
        population_size = population_size,
        population_range = (0,255),
    )

    objective_function = GripStrengthObjective(

    )

    crossover_mechanism = SimpleCrossover(
        crossover_point = 4
    )

    evolution_mechanism = LastNReplacement(
        n_replacement = 10,
        crossover_mechanism = crossover_mechanism
    )

    end_condition = MaxTrials(5)

    objective = GripStrengthObjective()
    random_scenarios = np.uint8(map_range(np.random.rand(1), 0, 255))
    scenario_list = list(map(objective.binary_to_scenario, random_scenarios))
    
    pprint(scenario_list)

    # batch_claw_test(scenario_list, max_processes=1)

    run_ga(
        initial_population = initial_population,
        objective_function = objective_function,
        evolution_mechanism = evolution_mechanism,
        end_condition = end_condition,
        )

    