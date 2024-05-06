from typing import Any
from random import randint
from numpy import uint8

class Crossover:
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.crossover_generation(*args, **kwds)

    def crossover(self, parent_1, parent_2):
        print("unimplemented crossover function")

    def crossover_generation(self, parent_list):
        child_list = []

        for parent_pair in parent_list:
            parent_1, parent_2 = parent_pair

            child_list += self.crossover(parent_1, parent_2)

        return child_list
    
class SimpleCrossover (Crossover):
    def __init__(self, crossover_point) -> None:
        self.crossover_point = crossover_point
    
    def crossover(self, parent_1, parent_2):
        mask = ~(parent_1 * uint8(0)) >> uint8(self.crossover_point)

        child_1 = (parent_1 & mask) | (parent_2 & ~mask) 
        child_2 = (parent_2 & mask) | (parent_1 & ~mask) 

        return [child_1, child_2]

class SingleRandomCrossover (SimpleCrossover):
    def __init__(self, gene_size) -> None:
        self.gene_size = gene_size
        super().__init__(0)

    def crossover(self, parent_1, parent_2):
        self.crossover_point = randint(0, self.gene_size)
        return super().crossover(parent_1, parent_2)
        
class MultiCrossover (Crossover):
    def __init__(self, crossover_point_list) -> None:
        # Note: must pass a list with an EVEN number of points
        self.crossover_interval_list = list(zip(
            crossover_point_list[::2],
            crossover_point_list[1::2]
        ))
        
    
    def crossover(self, parent_1, parent_2):

        zero = (parent_1 & uint8(0))
        nbits = zero.nbytes * 8
        mask = (parent_1 & uint8(0))

        for interval in self.crossover_interval_list:
            right_point, left_point = interval

            print(right_point, left_point)

            left_submask = ~zero >> uint8(nbits - left_point)
            right_submask = ~zero >> uint8(nbits - right_point)

            submask = left_submask & ~right_submask
            mask = mask | submask

        child_1 = (parent_1 & mask) | (parent_2 & ~mask) 
        child_2 = (parent_2 & mask) | (parent_1 & ~mask) 

        return [child_1, child_2]