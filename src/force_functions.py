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

def hybrid_growth(simulation_time, starting_value, lin_rate, exp_rate, *args, **kwargs):
    lin_growth = lin_rate * simulation_time
    exp_growth = exp_rate ** simulation_time
    output = starting_value * exp_growth + lin_growth
    return output

# Extract and process the growth data passed in
def extract_force_data(mode, **kwargs):
    # deligate the mode of growth to a lambda function
    if mode == "linear":
        growth_function = linear_growth
    elif mode == "exponential":
        growth_function = exponential_growth
    elif mode == "hybrid":
        growth_function = hybrid_growth
    
    growth_parameters = kwargs # give growth function necessary information given in passed_data

    return growth_function, growth_parameters
