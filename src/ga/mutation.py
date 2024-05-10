import numpy as np

class Mutation:
    def mutate(self, individual):
        print("unimplemented mutation function")
        
    def mutate_generation(self, generation):
        return list(map(self.mutate, generation))


class NoMutation:
    def __init__(self) -> None:
        pass

    def mutate(self, individual):
        return individual
    
class RandomMutation:
    def __init__(self, mutation_probability, gene_size) -> None:
        self.gene_size = gene_size
        self.mutation_probability = mutation_probability

    def mutate(self, individual):
        num_bits = individual.nbytes * 8
        for bit in range(num_bits):
            if np.random.rand(1)[0] < self.mutation_probability:
                individual = individual ^ (np.uint8(0x01) << np.uint8(bit))

        return individual
