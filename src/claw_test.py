from multiprocessing import Process, Lock, Pool
from time import time
import random

from test_actuator import TestActuator

from coppelia import *
from claws import *
from scenes import *

coppelia_path = (
    "/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev10_Ubuntu20_04/"
)

def init_process(lock):
    global startup_lock
    startup_lock = lock

def batch_claw_test(scenario_list, max_processes=100):
    startup_lock = Lock()

    # for scenario in scenario_list:
    #     scenario["startup_lock"] = startup_lock

    initializer_args = (startup_lock,)

    with Pool(max_processes, initializer=init_process, initargs=initializer_args) as p:
        p.map(run_scenario_dict, scenario_list)

    # batch = [
    #     Process(target=run_scenario, args=(startup_lock,), kwargs=scenario)
    #     for scenario in scenario_list
    # ]

    # [process.start() for process in batch]

    # [process.join() for process in batch]


def run_scenario_dict(scenario_dict):
    run_scenario(**scenario_dict)

def run_scenario(
    # startup_lock,
    scene,
    claw,
    actuator,
    log_file,
    headless=False,
    autoquit=False,
    *args,
    **kwargs,
):
    if startup_lock != None:
        startup_lock.acquire()

    sim = Sim(headless=headless)

    sim.api.loadScene(scene)
    sim.api.setInt32Parameter(sim.api.intparam_dynamic_engine, sim.api.physics_newton)

    attachment_point = sim.api.getObject(":/AttachmentPoint")  # find attachment point
    gripper = attach_gripper(
        sim, gripper_path=claw, attachment_point=attachment_point, offset=[0, 0.05, 0]
    )

    actuator = TestActuator(sim_api=sim.api, log_file=log_file, **actuator)

    if startup_lock != None:
        startup_lock.release()

    start = time()
    while time() < start + 1:
        sim.spin()

    sim.start()

    while not sim.get_exit_request() and not sim.is_stopped():
        t = sim.api.getSimulationTime()
        print(
            f"Simulation time: {t:.2f} [s] (simulation running synchronously to client, i.e. stepped)"
        )
        actuator.actuation_loop()
        actuator.sensor_loop()
        sim.step()

    sim.stop()

    # if not qutoquit, just run gui until user closes it
    while not autoquit and (not sim.get_exit_request()):
        sim.spin()

    print("Deinitializing =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
    sim.deinitialize()


def attach_gripper(sim, gripper_path, attachment_point, offset):
    gripper = sim.api.loadModel(gripper_path)
    sim.api.setObjectPosition(gripper, offset, attachment_point)
    sim.api.setObjectParent(gripper, attachment_point, True)
    return gripper


# Takes a list of strings (files or just strings) and formats them into a unique file name
def create_file_name(*files):
    file_name = (
        "_".join(
            [
                (
                    "".join(file.split("/")[-1].split(".")[0:-1])
                    if len(file.split(".")) > 1
                    else file
                )
                for file in files
            ]
        )
        + ".txt"
    )
    return file_name


# TODO: Make Louse Gripper Pad from an array of springs & small blocks to simulate compliant materials
# TODO: Increase size of pad overall (made from many small plates)
# TODO: Check if coppeliasim can check/output friction/contact points
# TODO: Start working on presentations
# TIMELINE:
# February: Add compliant pad and investigate contact area (correlation b/t grip area and force)
# Investigate rigid/flexible wrist in test scene
# First Week March --> meeting
# March: Complete in simulation --> optimizing and identifying positive quanifications
# April: Validate in real world test --> show comparrison: gap b/t simulation and real-world
# Result: does real-worl results follow the trend observied in simulation
# use GA AI to optimize effects
def main():
    # claw_list = all_claws
    # claw_list = [Louse_Pad]
    claw_list = bio_claws
    # scene_list = all_scenes
    scene_list = [flex_pole_scene_5cm]
    actuator_list = ["VerticalForce", "HorizontalForce"]
    # actuator_list = ['VerticalForce']
    # actuator_list = ['HorizontalForce']
    reps = 10

    force = {
        "starting_value": 0.0,
        "mode": "hybrid",
        "lin_rate": 1.0,
        "exp_rate": 1.05,
    }

    scenario_list = [
        {
            "scene": scene,
            "claw": claw,
            "actuator": {
                "name": actuator,
                "force": force,
                "wait_time": 1.0,
                "position_threshold": 0.1,
            },
            "log_file": create_file_name(scene, claw, actuator),
            "headless": True,
            "autoquit": True,
        }
        for scene in scene_list
        for claw in claw_list
        for actuator in actuator_list
    ] * reps
    random.shuffle(scenario_list)
    batch_claw_test(scenario_list=scenario_list, max_processes=2)


if __name__ == "__main__":
    main()
