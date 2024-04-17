# python
import sys

sys.path.append("/home/nathan/Documents/GitHub/Bio-Inspired-Foot-Design/src")
from coppeliasim_utils import set_torque, set_spring_constants, duplicate_objects

sim = None
claw_info = {}

X = 0
Y = 1
Z = 2


def sysCall_init():
    global sim, claw_info
    sim = require("sim")

    claw_info = {
        "hook_motor": sim.getObject("./ForceSensor[1]/Base/ForceSensor/Cuboid/Active"),
        "pad_base_spring": sim.getObject("./ForceSensor[1]/Base/Flex[0]"),
        "pad_base_solid": sim.getObject("./ForceSensor[1]/Base/Flex[0]/Cylinder"),
        "pad_unit_list": [],
    }

    claw_info["pad_unit_list"] = [
        (claw_info["pad_base_spring"], claw_info["pad_base_solid"])
    ]


def set_claw_torques(motor_torque):
    global sim, claw_info
    motor_list = ["hook_motor"]

    for motor in motor_list:
        set_torque(sim, claw_info[motor], motor_torque)

def set_pad_strength(k, c):
    global sim, claw_info
    for unit in claw_info["pad_unit_list"]:
        spring = unit[0]
        set_spring_constants(sim, spring, k, c)


def set_pad_size(num_units):
    global sim, claw_info
    max_units = 8
    if num_units > max_units:
        print("Cannot create more than 8 pad units! limiting to 8")
        num_units = 8

    num_units = num_units - 1  # base unit prexists

    max_left_units = 2
    num_left_units = min(max_left_units, int(num_units / 2))
    num_right_units = num_units - num_left_units

    clear_pad()

    if -1 == num_units:
        remove_pad_unit(0)

    right_offset = [0, 0.05, 0.025]
    left_offset = [0, -0.05, 0.03]

    
    for unit in range(num_right_units):
        create_pad_unit(mul_list(right_offset, unit + 1))

    for unit in range(num_left_units):
        create_pad_unit(mul_list(left_offset, unit + 1))


def mul_list(list, mul):
    return [num * mul for num in list]


def create_pad_unit(offset):
    global sim, claw_info
    base_unit = claw_info["pad_unit_list"][0] 
    new_pad_unit = duplicate_objects(sim, base_unit, offset, base_unit[0])

    sim.setJointTargetPosition(new_pad_unit[0], 0.2 - (offset[Z]*1.6))
    sim.setJointPosition(new_pad_unit[0], 0)

    claw_info["pad_unit_list"].append(new_pad_unit)

def clear_pad():
    global sim, claw_info
    while True:
        pad_units = len(claw_info["pad_unit_list"])

        if 1 == pad_units:
            return

        remove_pad_unit(1)


def remove_pad_unit(unit):
    global sim, claw_info
    sim.removeObjects(claw_info["pad_unit_list"][unit])
    del claw_info["pad_unit_list"][unit]


def sysCall_actuation():
    # put your actuation code here
    pass


def sysCall_sensing():
    # put your sensing code here
    pass


def sysCall_cleanup():
    # do some clean-up here
    pass


# See the user manual or the available code snippets for additional callback functions and details
