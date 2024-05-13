import multiprocessing
import threading
from time import time, sleep
import random
import asyncio
import os
import sys
from pprint import pprint
from copy import deepcopy

from coppeliasim_utils import *
from coppeliasim_wrapper import run_coppeliasim

from test_actuator import TestActuator

from coppelia_files.claws import *
from coppelia_files.scenes import *


coppelia_path = (
    "/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev18_Ubuntu20_04/"
)


def init_process(lock):
    global startup_lock
    startup_lock = lock


def batch_claw_test(scenario_list, max_processes=6, vary_actuator=False):
    startup_lock = multiprocessing.Lock()
    initializer_args = (startup_lock,)

    with multiprocessing.Pool(
        max_processes, initializer=init_process, initargs=initializer_args
    ) as p:
        if vary_actuator:
            scenario_list = create_double_scenario_list(scenario_list)

            all_results = list(p.map(run_scenario_dict, scenario_list))

            num_scenarios = len(scenario_list)
            results1 = all_results[0:num_scenarios]
            results2 = all_results[num_scenarios:]

            return results1, results2
        
        else:
            results = list(p.map(run_scenario_dict, scenario_list))
            # results = list(map(run_scenario_dict, scenario_list))
            return results
    # for scenario in scenario_list:
    #     run_scenario_dict(scenario)

def create_double_scenario_list(scenario_list):
    vertical_scenarios = deepcopy(scenario_list)
    for scenario in vertical_scenarios:
        scenario['actuator']['name'] = "VerticalForce"

    horizontal_scenarios = deepcopy(scenario_list)
    for scenario in horizontal_scenarios:
        scenario['actuator']['name'] = "HorizontalForce"

    return vertical_scenarios + horizontal_scenarios

def run_scenario_dict(scenario_dict):
    return run_scenario(**scenario_dict)


def run_scenario(
    claw_scenario,
    actuator,
    *args,
    **coppelia_kwargs,
):
    startup_lock.acquire()

    port = find_free_port()
    coppelia_kwargs["port"] = port
    coppelia_kwargs["num_timesteps"] = 10e5
    coppelia_thread = threading.Thread(target=run_coppeliasim, kwargs=coppelia_kwargs)
    coppelia_thread.start()

    sim = connect_to_api(port)  # will block until loaded

    sim.setInt32Parameter(sim.intparam_dynamic_engine, sim.physics_newton)
    
    startup_lock.release()
    
    attachment_point = sim.getObject(":/AttachmentPoint")  # find attachment point

    gripper = attach_gripper(
        sim,
        claw_scenario=claw_scenario,
        attachment_point=attachment_point,
        offset=[0, 0.05, 0],
    )

    actuator = TestActuator(sim_api=sim, **actuator)

    sim.setStepping(True)

    sim.startSimulation()

    modify_gripper(sim, gripper, **claw_scenario)
    actuator_force = 0

    while not is_stopped(sim):
        t = sim.getSimulationTime()
        # print(
        #     f"Simulation time: {t:.2f} [s] (simulation running synchronously to client, i.e. stepped)"
        # )
        actuator_force = actuator.actuation_loop()
        actuator.sensor_loop()
        sim.step()

    return actuator_force


def attach_gripper(sim, claw_scenario, attachment_point, offset):
    gripper = create_gripper(sim, **claw_scenario)
    sim.setObjectPosition(gripper, offset, attachment_point)
    sim.setObjectParent(gripper, attachment_point, True)
    return gripper


def create_gripper(sim, path, *args, **kwargs):
    object_handle = sim.loadModel(path)

    return object_handle


def modify_gripper(sim, object_handle, *args, **kwargs):
    script_handle = sim.getScript(sim.scripttype_childscript, object_handle)

    asyncio.run(
        handle_louse_options(
            sim,
            object_handle=object_handle,
            script_handle=script_handle,
            *args,
            **kwargs,
        )
    )


    handle_finger_options(
        sim, object_handle=object_handle, script_handle=script_handle, *args, **kwargs
    )



async def async_call_script_function(sim, function_name, script_handle, *params):
    await sim.callScriptFunction("set_pad_size", script_handle, *params)


async def handle_louse_options(
    sim,
    script_handle,
    num_pad_units=None,
    pad_strength=None,
    pad_starting_pos=0,
    curvature=None,
    scale=None,
    claw_torque=None,
    *args,
    **kwargs,
):
    if pad_strength is not None:
        call_script_function(sim, "set_pad_strength", script_handle, *pad_strength)

    if num_pad_units is not None:
        sim.callScriptFunction("set_pad_size", script_handle, num_pad_units, pad_starting_pos)

    if curvature is not None:
        call_script_function(sim, "set_curvature", script_handle, curvature)

    if scale is not None:
        call_script_function(sim, "set_link_scale", script_handle, scale)

    if claw_torque is not None:
        sim.callScriptFunction("set_claw_torques", script_handle, claw_torque)

    


def handle_finger_options(
    sim, script_handle, claw_torque=None, flex_strength=None, *args, **kwargs
):
    if claw_torque is not None:
        sim.callScriptFunction("set_claw_torques", script_handle, claw_torque)

    if flex_strength is not None:
        sim.callScriptFunction("set_flex_values", script_handle, *flex_strength)


def create_metadata_string(item):
    if type(item) is str:
        if os.path.exists(item):
            return "scene=" + extract_file_name(item)
        else:
            return "applied_force=" + item

    if type(item) is dict:
        return ":".join(
            [key + "=" + str(simplify_dict_item(item[key])) for key in item]
        )


def simplify_dict_item(value):
    if type(value) is tuple:
        return value[0]
    elif type(value) is str:
        if os.path.exists(value):
            return extract_file_name(value)

    return value


def simplify_item(item):
    if os.path.exists(item):
        return extract_file_name(item)
    else:
        return item


def extract_file_name(file_path):
    return "".join(file_path.split("/")[-1].split(".")[0:-1])


# Takes a list of strings (files or just strings) and formats them into a unique file name
def create_file_name(*metadata_fields):
    metadata = [create_metadata_string(item) for item in metadata_fields]

    file_name = ":".join(metadata) + ".txt"

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

# TODO: Edit friction coefficients for claw:
# Pad: hig hfriction
# Hook: Low Friction --> should affect rigid most
# TODO: What if we put the pad along the whole finger
# See: without pad, it has certain performance, with whole pad, different performance, with partial pad, middle performance
# on top of stiffness
# Could be evolved: % of covered area

def pack_scenario(**kwargs):
    return kwargs

def create_basic_claw_scenario_list(claw_list):
    return [{"path": path} for path in claw_list]


def create_louse_scenario_list():
    # num_pad_unit_list = [0, 2, 4, 6, 8]
    num_pad_unit_list = [6]
    pad_strength_list = [
        (5, 5),
        (15, 10),
        (30, 10),
        (45, 10),
        (90, 10),
        (135, 10),
    ]

    scenario_list = [
        {
            "path": Louse_Pad_Script,
            "num_pad_units": num_pad_units,
            "pad_strength": pad_strength,
        }
        for num_pad_units in num_pad_unit_list
        for pad_strength in pad_strength_list
    ]

    return scenario_list


def create_finger_scenario_list():
    flex_strength_list = [
        (5, 0.1),
        (15, 0.1),
        (30, 0.1),
        (45, 0.1),
        (90, 0.1),
        (135, 0.1),
        (270, 0.1),
    ]

    scenario_list = [
        {
            "path": Finger_Flex_Script,
            "flex_strength": flex_strength,
        }
        for flex_strength in flex_strength_list
    ]

    return scenario_list


if __name__ == "__main__":
    claw_list = all_claws
    # claw_list = [Louse_Pad]
    # claw_list = bio_claws
    # claw_scenario_list = create_basic_claw_scenario_list(claw_list)
    # claw_scenario_list = create_louse_scenario_list() + create_finger_scenario_list()
    claw_scenario_list = create_louse_scenario_list()
    # claw_scenario_list = create_finger_scenario_list()

    # scene_list = all_scenes
    scene_list = [flex_pole_scene_5cm]
    actuator_list = ["VerticalForce", "HorizontalForce"]
    # actuator_list = ['VerticalForce']
    # actuator_list = ['HorizontalForce']
    reps = 10

    force = {
        "starting_value": 1.0,
        "mode": "hybrid",
        "lin_rate": 500.0,
        "exp_rate": 1.1,
    }

    scenario_list = [
        {
            "scene": scene,
            "claw_scenario": claw_scenario,
            "actuator": {
                "name": actuator,
                "force": force,
                "wait_time": 1.0,
                "position_threshold": 0.1,
            },
            # "log_file": create_file_name(scene, claw_scenario, actuator),
            "headless": False,
            "autoquit": True,
        }
        for scene in scene_list
        for claw_scenario in claw_scenario_list
        for actuator in actuator_list
    ] * reps

    random.shuffle(scenario_list)

    scenario_list = scenario_list[0:5]


    print("results: ", batch_claw_test(scenario_list=scenario_list, max_processes=4))
