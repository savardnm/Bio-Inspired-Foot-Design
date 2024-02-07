import sys
sys.path.append('/home/nathan/Documents/GitHub/Bio-Inspired-Foot-Design/src')
from coppeliasim_wrapper import *
import subprocess

coppelia_path="/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev10_Ubuntu20_04/"

scene_dir = coppelia_path + "scenes/stickbug/"
gripper_dir = coppelia_path + "models/stickbug/"

pole_scene = scene_dir + "05_Pole_Test_detached_python.ttt"
finger_gripper_path = gripper_dir + "FingerClaw.ttm"



def main():
    passed_data = {
        "gripper":finger_gripper_path,
        "wait_time":1.0,
        "vertical_actuator": {
            "force":{
                "starting_value": 1.0,
                "mode":"linear",
                "rate":5.0
            },
            "position_threshold":0.1
        }
    }

    result = simulate(scene=pole_scene, passed_data=passed_data, num_timesteps=5e5, autoquit=True, headless=False)

    print(get_stdout(result))

def filter_final_values(coppelia_result):
    filtered_result = subprocess.run(["grep", "Final"], input=coppelia_result.stdout, capture_output=True)

    return filtered_result


if __name__ == "__main__":
    main()