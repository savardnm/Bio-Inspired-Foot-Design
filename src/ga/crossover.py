from typing import Any
from numpy import *
class SimpleCrossover:
    def __init__(self, crossover_point) -> None:
        self.crossover_point = crossover_point
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.crossover_generation(*args, **kwds)

    def crossover_generation(self, parent_list):
        child_list = []

        for i, _ in enumerate(parent_list):
            if (i % 2):
                continue
            
            parent_1 = parent_list[i]
            parent_2 = parent_list[i+1]

            child_list += self.crossover(parent_1, parent_2)

        return child_list

    def crossover(self, parent_1, parent_2):
        mask = ~(parent_1 * uint8(0)) >> uint8(self.crossover_point)

        child_1 = (parent_1 & mask) | (parent_2 & ~mask) 
        child_2 = (parent_2 & mask) | (parent_1 & ~mask) 

        return [child_1, child_2]

        
        
