from force_functions import *
import sys
from logger import log


class TestActuator:
    def __init__(self, sim_api, name, force, log_file=None, wait_time=0.0, position_threshold=0.0, *args, **kwargs) -> None:
        self.sim_api = sim_api
        print("searching for " + name + " in scene")
        self.name = name
        self.handle=sim_api.getObject(":/" + name)
        
        self.milestone = max(force['starting_value'], 0.1)
        self.force_function, self.force_parameters = extract_force_data(**force)

        self.wait_time = wait_time

        self.position_threshold = position_threshold
        self.log_file = log_file

        self.active = True
            

    def actuation_loop(self):
        simulation_time = self.sim_api.getSimulationTime()


        force_value = self.force_function(simulation_time - self.wait_time, **self.force_parameters)
        if simulation_time < self.wait_time:
            force_value = 0.0 # wait before grasping
        else:
            self.sim_api.setJointForce(self.handle, force_value)

    def sensor_loop(self):
        self.check_position_threshold()


    def check_position_threshold(self):
        if self.active == False:
            return 
        actuator_position = self.sim_api.getJointPosition(self.handle)
        actuator_force = self.sim_api.getJointForce(self.handle)
        simulation_time = self.sim_api.getSimulationTime()

        if actuator_force != None and abs(actuator_force) > self.milestone:
            print("[%0.2fs]"%simulation_time, "\t" + self.name + " force:%0.2fN"%actuator_force)
            self.milestone = self.milestone * 2

        if actuator_position != None and actuator_position < self.position_threshold:
            self.active = False
            log("[%0.2fs]"%simulation_time, "\t" + self.name + " final force:%0.2fN"%actuator_force, file=self.log_file)
            print("Gripper Failed. Stopping Simulation...")
            self.sim_api.stopSimulation()