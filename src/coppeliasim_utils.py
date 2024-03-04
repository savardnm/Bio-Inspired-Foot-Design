from threading import Thread
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

def is_stopped(sim):
    return sim.getSimulationState() == sim.simulation_stopped

def step(sim):
    if sim.getSimulationState() != sim.simulation_stopped:
        t = sim.getSimulationTime()
        while t == sim.getSimulationTime():
            spin(sim)

def spin(sim):
    sim.simLoop(None, 0)


def connect_to_api(port):
    client = RemoteAPIClient(port=port)
    sim = client.require('sim')
    return sim

def set_torque(sim, object, motor_torque):
    sim.setJointTargetForce(object, motor_torque)


def set_spring_constants(sim, object, k, c):
    # global sim
    sim.setObjectFloatParam(object, sim.jointfloatparam_kc_k, k)
    sim.setObjectFloatParam(object, sim.jointfloatparam_kc_c, c)


def duplicate_objects(sim, object_list, offset=[0, 0, 0], offset_frame=None):
    copied_objects = sim.copyPasteObjects(object_list, 0)

    if offset:  # if chosen, automatically parent the copied objects at a given offset
        base = sim.getObjectParent(object_list[0])
        if not offset_frame:
            offset_frame = base

        sim.setObjectPosition(copied_objects[0], offset, offset_frame)
        sim.setObjectParent(copied_objects[0], base, True)

    return copied_objects


def call_script_function(sim, function_name, script_handle, *args):
    sim.callScriptFunction(function_name, script_handle, *args)

import socket
from contextlib import closing

def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]
