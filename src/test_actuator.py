from force_functions import *
import sys
import logger

class TestActuator:
    def __init__(self, sim, name, passed_data, handle) -> None:
        self.sim = sim
        self.name = name
        self.handle=handle

        self.log_file = passed_data["output_file"]

        self.active = name in passed_data
        if self.active:
            self.passed_data = passed_data[name]

        self.milestone = 1.0
            

    def actuation_loop(self):
        if not self.active:
            return # only actuate if active

        simulation_time = self.sim.getSimulationTime()

        force_function, force_parameters = extract_force_data(**self.passed_data['force'])

        force_value = force_function(simulation_time, **force_parameters)

        if "wait_time" in self.passed_data:
            if simulation_time < self.passed_data["wait_time"]:
                force_value = 0.0 # wait for 1 sec for setup and grasping
        
        self.sim.setJointForce(self.handle, force_value)

    def sensor_loop(self):
        if not self.active:
            return # only sense if active
        
        self.check_position_threshold(**self.passed_data)


    
    def check_position_threshold(self, position_threshold, *args, **kwargs):
        actuator_position = self.sim.getJointPosition(self.handle)
        actuator_force = self.sim.getJointForce(self.handle)
        simulation_time = self.sim.getSimulationTime()

        if abs(actuator_force) > self.milestone:
            logger.log(self.log_file, "[%0.2fs]"%simulation_time, "\t" + self.name + " force:%0.2fN"%actuator_force)
            self.milestone = self.milestone * 2

        if actuator_position < position_threshold:
            logger.log(self.log_file, "[%0.2fs]"%simulation_time, "\t" + self.name + " final force:%0.2fN"%actuator_force)
            logger.log(self.log_file, "Actuator Failed. Stopping Simulation...")
            self.sim.stopSimulation()
            self.active = False