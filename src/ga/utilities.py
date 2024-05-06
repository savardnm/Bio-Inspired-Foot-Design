from numpy import uint8

def map_range(input_value, min_value, max_value, *args, **kwargs):
    input_value = normalize_value(input_value, *args, **kwargs)
    return (input_value * (max_value - min_value)) + min_value # Scale


def normalize_value(input_value, min_input=0.0, max_input=1.0, *args, **kwargs):
    return (input_value - min_input) / (max_input - min_input) # Normalize

def extract_gene(binary, start_bit, end_bit):
    start_bit = uint8(start_bit)
    end_bit = uint8(end_bit)
    zeros = binary & uint8(0)
    ones = ~zeros
    lower_bound = ones << start_bit
    upper_bound = ~(ones << end_bit)
    mask = lower_bound & upper_bound
    masked_binary = binary & mask
    extracted_number = masked_binary >> start_bit
    return extracted_number