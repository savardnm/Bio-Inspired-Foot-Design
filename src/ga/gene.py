from numpy import *

class SingleValueGene:
    def __init__(self, value: uint8=None, binary=None) -> None:
        if value is not None:
            self.value = value

        if binary is not None:
            self.value = self.construct_from_binary(binary)

    def deconstruct_to_binary(self):
        return self.value
    
    def construct_from_binary(self, binary):
        return binary