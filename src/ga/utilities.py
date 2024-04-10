def map_range(input_value, min_value, max_value, *args, **kwargs):
    input_value = normalize_value(input_value, *args, **kwargs)
    return (input_value * (max_value - min_value)) + min_value # Scale


def normalize_value(input_value, min_input=0.0, max_input=1.0, *args, **kwargs):
    return (input_value - min_input) / (max_input - min_input) # Normalize
