from force_functions import *

class actuator:
    def __init__(self, sim, name, passed_data) -> None:
        self.sim = sim
        self.name = name
        self.passed_data = passed_data

    def actuation_loop(self):
        if not self.name in self.passed_data:
            return # only sense if active

        simulation_time = self.sim.getSimulationTime()

        force_function, force_parameters = extract_force_data(**self.passed_data[name]['force'])

        force_value = force_function(simulation_time, **force_parameters)

        if "wait_time" in self.passed_data:
            if simulation_time < self.passed_data["wait_time"]:
                force_value = 0.0 # wait for 1 sec for setup and grasping
        
        self.sim.setJointForce(actuator, force_value)

    def sensor_loop(self):
        pass

