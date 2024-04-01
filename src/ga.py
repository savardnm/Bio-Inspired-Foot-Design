

def run_ga():
    population = initialization()

    while not end_condition_met():

        population_results = objective_function(population)
        
        selected_population = selection(population_results)

        population = crossover(selected_population)


def selection(objective_results):
    return 


def end_condition_met():
    return False

def initialize_population():
    initial_population = None
    return initial_population

if __name__ == '__main__':
    test_population = TestPopulation()
    run_ga()