from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import numpy as np

def is_stopped(sim):
    return (sim.getSimulationState() == sim.simulation_stopped) or (sim.getSimulationState() == sim.simulation_paused)

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
    print("set torque")


def set_spring_constants(sim, object, k, c):
    # global sim
    sim.setObjectFloatParam(object, sim.jointfloatparam_kc_k, k)
    sim.setObjectFloatParam(object, sim.jointfloatparam_kc_c, c)

def get_all_objects(sim, object_search_string):
    i = 0
    object_handle_list = []
    while True:
        next_object = sim.getObject(object_search_string, {'index': i, 'noError': True})
        if next_object < 0:
            break
        object_handle_list.append(next_object)
        i = i + 1
    return object_handle_list

def get_all_children(sim, object_handle):
    i = 0
    child_list = []
    while True:
        next_object = sim.getObjectChild(object_handle, i)
        if next_object < 0:
            break
        child_list.append(next_object)
        i = i + 1
    return child_list

def rotate_object(sim, object_handle, axis, angle, local=False):
    print("rotating!!!! <<<")
    object_position = sim.getObjectPosition(object_handle)
    object_pose = sim.getObjectPose(object_handle)

    if local:
        # if local, use a single local axis (x: 0, y: 1, or z: 2) instead of the axis vector
        object_pose_matrix = sim.getObjectMatrix(object_handle)
        object_pose_matrix = np.reshape(object_pose_matrix, (3,4))
        print("pose: ", object_pose_matrix, "\naxis", axis, "\nnew axis: " )
        print(np.array(object_pose_matrix)[0:3, axis])
        axis = np.array(object_pose_matrix)[0:3, axis].tolist()

    object_pose_rotated = sim.rotateAroundAxis(object_pose, axis, object_position, angle)


    sim.setObjectPose(object_handle, object_pose_rotated)
    sim.auxiliaryConsolePrint(0, "string text")
    # print(object_handle, axis, rotation, local)

def duplicate_objects(sim, object_list, offset=[0, 0, 0], offset_frame=None):
    copied_objects = sim.copyPasteObjects(object_list, 0)

    if offset:  # if chosen, automatically parent the copied objects at a given offset
        base = sim.getObjectParent(object_list[0])
        if not offset_frame:
            offset_frame = base

        sim.setObjectPosition(copied_objects[0], offset, offset_frame)
        sim.setObjectParent(copied_objects[0], base, True)

    return copied_objects

def scale_object(sim, object_handle, scale):
    print('handle:', object_handle, '\nscale:', scale)
    sim.scaleObject(object_handle, scale[0], scale[1], scale[2])
    

def move_object(sim, object_handle, offset, frame=None):
    if None == frame:
        frame = object_handle

    starting_pos = sim.getObjectPosition(object_handle, frame)
    ending_pos = (np.array(starting_pos) + np.array(offset)).tolist()

    print("moving", object_handle,"from",starting_pos,"to", ending_pos)

    sim.setObjectPosition(object_handle, ending_pos, frame)

def call_script_function(sim, function_name, script_handle, *args):
    sim.callScriptFunction(function_name, script_handle, *args)

import socket
from contextlib import closing
from random import randint

def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]
