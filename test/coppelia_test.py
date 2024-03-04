import sys
sys.path.append('/home/nathan/Documents/GitHub/Bio-Inspired-Foot-Design/src')
from coppeliasim_wrapper import *
import subprocess
from multiprocessing import Pool
from copy import deepcopy
import os

coppelia_path="/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev18_Ubuntu20_04/"
results_path="/home/nathan/Documents/GitHub/Bio-Inspired-Foot-Design/results"

scene_dir = coppelia_path + "scenes/stickbug/"
gripper_dir = coppelia_path + "models/stickbug/"

pole_scene = scene_dir + "05_Pole_Test_detached_python.ttt"
finger_gripper_path = gripper_dir + "FingerClaw.ttm"
hook_gripper_path = gripper_dir + "HookClaw.ttm"



def main():
    passed_data = {
        'gripper':finger_gripper_path,
        'horizontal_actuator': {
            'wait_time':1.0,
            'force':{
                'starting_value': 1.0,
                'mode':'linear',
                'rate':5.0
            },
            'position_threshold':0.1
        },
        'output_file':results_path + '/output.txt'
    }


    trials = construct_trials()

    # trials = [trials[0]]

    with Pool(1) as pool:
        pool.map(run_test, trials)
    # for trial in trials:
    #     run_test(trial)

    print("done")
    # result = simulate(scene=pole_scene, passed_data=passed_data, num_timesteps=5e5, autoquit=True, headless=False)
    # print("STDOUT ===============\n", get_stdout(result), "==============")

def run_test(data):
    print("Running test with data:\n", data, "\n===============\n")
    return simulate(scene=data["scene"], passed_data=data["passed_data"], num_timesteps=5e5, autoquit=True, headless=False)

def construct_trials():

    trials = [{"scene":pole_scene,"passed_data":{}} for i in range(4)]

    for i in [0,1]:
        trials[i]["passed_data"]["gripper"] = finger_gripper_path
        trials[i]["passed_data"]["output_file"] = results_path + "/Finger_"
    for i in [2,3]:
        trials[i]["passed_data"]["gripper"] = hook_gripper_path
        trials[i]["passed_data"]["output_file"] = results_path + "/Hook_"

    for i in [0,2]:
        trials[i]["passed_data"]["vertical_actuator"] = {
            'wait_time':1.0,
            'force':{
                'starting_value': 1.0,
                'mode':'linear',
                'rate':5.0
            },
            'position_threshold':0.1
        }
        trials[i]["passed_data"]["output_file"] = trials[i]["passed_data"]["output_file"] + "Shear.txt"
    for i in [1,3]:
        trials[i]["passed_data"]["horizontal_actuator"] = {
            'wait_time':1.0,
            'force':{
                'starting_value': 1.0,
                'mode':'linear',
                'rate':5.0
            },
            'position_threshold':0.1
        }
        trials[i]["passed_data"]["output_file"] = trials[i]["passed_data"]["output_file"] + "Normal.txt"

    for i in range(4):
        trials[i]['passed_data']['output_file'] = unique_index_file(trials[i]['passed_data']['output_file'])

    # for trial in trials:
    #     print("Trial ", trial, "\n ------------------------")

    return trials


def filter_final_values(coppelia_result):
    filtered_result = subprocess.run(["grep", "Final"], input=coppelia_result.stdout, capture_output=True)
    return filtered_result

def unique_index_file(file_path):
    index = 0
    split_file_path = file_path.split(".")
    file_ext = split_file_path[-1]
    file_name = "".join(split_file_path[0:-1])
    
    while True:
        suffix = "%03d"%index
        unique_file_path = "".join([file_name, "_", suffix, ".", file_ext])
        if not os.path.exists(unique_file_path):
            return unique_file_path
        index += 1
        
    



if __name__ == "__main__":
    main()