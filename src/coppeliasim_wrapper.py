import subprocess
import json
from multiprocessing import Process

# ./coppeliaSim.sh -q -h -s500000 -gmodels/stickbug/FingerClaw.ttm -g10 -g0 scenes/stickbug/05_Pole_Test_detached.ttt
path_to_compeliasim = "/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev10_Ubuntu20_04/coppeliaSim.sh"
path_to_python_coppeliasim = "/home/nathan/Documents/GitHub/Bio-Inspired-Foot-Design/src/coppelia.py"

def encode_passed_data(data_dict):
    data_string = str(data_dict)
    
    corrected_data_string = data_string.replace("'", '"').replace(" ", "")
    # corrected_data_string = "'" + corrected_data_string + "'"

    data_flag = "-g" + corrected_data_string
    return data_flag

def decode_passed_data(data_string):
    print("data_string: ", data_string)
    data_dict = json.loads(data_string)
    return data_dict

def retrieve_passed_data(sim):
    passed_data_string = sim.getStringParameter(sim.stringparam_app_arg1)
    passed_data = decode_passed_data(passed_data_string)
    return passed_data

def launch():
    simulate(headless=False, autoquit=False)
    

def simulate(scene=None, num_timesteps=5e5, autoquit=True, passed_data=None, headless=True, target="sh"):
    flags = []
    data = {}


    if target == "sh":
        command = [path_to_compeliasim]
    if target == "py":
        command = ["/usr/bin/python3", path_to_python_coppeliasim]

    if autoquit:
        flags.append("-q")

    if headless:
        flags.append("-H")

    if num_timesteps != None:
        flags.append("-s" + str(int(num_timesteps)))

    if scene != None:
        flags.append(scene)

    if passed_data:
        flags.append(encode_passed_data(passed_data))

    command_array = command + flags

    print(">", *command_array)
    
    result = subprocess.run(command_array, stdout=subprocess.PIPE)

    return result

def get_stdout(coppelia_result):
    return coppelia_result.stdout.decode()

def main():
    launch()
    pass

if __name__ == "__main__":
    main()

