from multiprocessing import Process, Lock, Pool
from time import time
import random
import asyncio

from coppeliasim_utils import call_script_function

from test_actuator import TestActuator

from coppelia import *
from claws import *
from scenes import *

import os

coppelia_path = (
    "/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev18_Ubuntu20_04/"
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
    claw_scenario,
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

    print("attaching gripper ====================")

    gripper = attach_gripper(
        sim,
        claw_scenario=claw_scenario,
        attachment_point=attachment_point,
        offset=[0, 0.05, 0],
    )


    print("================== attached gripper")

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


def attach_gripper(sim, claw_scenario, attachment_point, offset):
    print("Creating gripper ============")
    gripper = create_gripper(sim, **claw_scenario)
    print("================= Created gripper")
    sim.api.setObjectPosition(gripper, offset, attachment_point)
    sim.api.setObjectParent(gripper, attachment_point, True)
    return gripper


def create_gripper(sim, path, *args, **kwargs):
    print("attempting to spawn object: ", path)
    object_handle = sim.api.loadModel(path)
    print("spawned object: ", object_handle)

    modify_gripper(sim, object_handle, *args, **kwargs)

    print("gripper modified object")

    return object_handle

def modify_gripper(sim, object_handle, *args, **kwargs):
    script_handle = sim.api.getScript(sim.api.scripttype_childscript, object_handle)
    print("fetched script handle: ", script_handle)

    asyncio.run(handle_louse_options(
        sim, object_handle=object_handle, script_handle=script_handle, *args, **kwargs
    ))

    print("louse options handled")

    handle_finger_options(
        sim, object_handle=object_handle, script_handle=script_handle, *args, **kwargs
    )

    print("finger options handled")


async def async_call_script_function(sim, function_name, script_handle, *params):
    await sim.api.callScriptFunction("set_pad_size", script_handle, *params)
    print("sim script done")


async def handle_louse_options(
    sim,
    script_handle,
    num_pad_units=None,
    pad_strength=None,
    claw_torque=None,
    *args,
    **kwargs,
):
    # print(sim.api.setStepping(False))
    if num_pad_units is not None:
        print("setting pad size to: ", num_pad_units)
        call_script_function(sim, "set_pad_size", script_handle, num_pad_units)
        # sim.api.executeScriptString("set_pad_size(num_pad_units)", script_handle)
        # async_call_script_function(sim, "set_pad_size", script_handle, num_pad_units)
        print("set pad size to: ", num_pad_units)

    if pad_strength is not None:
        # sim.api.callScriptFunction("set_pad_strength", script_handle, *pad_strength)
        print("set pad strength to: ", pad_strength)

    if claw_torque is not None:
        # sim.api.callScriptFunction("set_claw_torques", script_handle, claw_torque)
        print("set torque to: ", claw_torque)



def handle_finger_options(
    sim, script_handle, claw_torque=None, flex_strength=None, *args, **kwargs
):
    if claw_torque is not None:
        sim.api.callScriptFunction("set_claw_torques", script_handle, claw_torque)

    if flex_strength is not None:
        sim.api.callScriptFunction("set_flex_values", script_handle, *flex_strength)


def create_metadata_string(item):
    if type(item) is str:
        if os.path.exists(item):
            return extract_file_name(item)
        else:
            return item

    if type(item) is dict:
        return "-".join(
            [simplify_key(key) + "=" + str(item[key]) + ":" for key in item]
        )


def simplify_key(key):
    return str(key).replace("_", "")


def extract_file_name(file_path):
    return "".join(file_path.split("/")[-1].split(".")[0:-1])


# Takes a list of strings (files or just strings) and formats them into a unique file name
def create_file_name(*metadata_fields):
    metadata = [create_metadata_string(item) for item in metadata_fields]

    file_name = "_".join(metadata) + ".txt"
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
    num_pad_unit_list = [0, 3, 5, 8]
    pad_strength_list = [
        (5, 5),
        (15, 10),
        (45, 10),
        (135, 10),
        (405, 10),
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
        (45, 0.1),
        (90, 0.1),
        (135, 0.1),
        (270, 0.1),
        (405, 0.1),
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
    claw_scenario_list = create_louse_scenario_list() + create_finger_scenario_list()

    scene_list = all_scenes
    scene_list = [flex_pole_scene_5cm]
    actuator_list = ["VerticalForce", "HorizontalForce"]
    # actuator_list = ['VerticalForce']
    # actuator_list = ['HorizontalForce']
    reps = 1

    force = {
        "starting_value": 0.0,
        "mode": "hybrid",
        "lin_rate": 1.0,
        "exp_rate": 1.05,
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
            "log_file": create_file_name(scene, claw_scenario, actuator),
            "headless": False,
            "autoquit": True,
        }
        for scene in scene_list
        for claw_scenario in claw_scenario_list
        for actuator in actuator_list
    ] * reps
    random.shuffle(scenario_list)

    print("first scenario:",  scenario_list[0])

    batch_claw_test(scenario_list=scenario_list, max_processes=1)

