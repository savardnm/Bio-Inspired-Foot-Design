def constant(starting_value, *args, **kwargs):
    return starting_value

def linear_growth(simulation_time, starting_value, rate, *args, **kwargs):
    
    growth = rate * simulation_time
    output = starting_value + growth
    return output

def exponential_growth(simulation_time, starting_value, rate, *args, **kwargs):
    growth = rate ** simulation_time
    output = starting_value * growth
    return output

# Extract and process the growth data passed in
def extract_force_data(mode, **kwargs):
    # deligate the mode of growth to a lambda function
    if mode == "linear":
        growth_function = linear_growth
    elif mode == "exponential":
        growth_function = exponential_growth
    
    growth_parameters = kwargs # give growth function necessary information given in passed_data

    return growth_function, growth_parameters
