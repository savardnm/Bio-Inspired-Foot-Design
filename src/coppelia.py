# need to set DYLD_LIBRARY_PATH=$PWD/../Frameworks
# to avoid libraries load errors
import argparse
import builtins
import os
import sys
import threading
import multiprocessing
from time import sleep
from datetime import datetime

from pathlib import Path
from ctypes import *

def sim_start(sim):
    if sim.getSimulationState() == sim.simulation_stopped:
        sim.startSimulation()

def sim_step(sim):
    if sim.getSimulationState() != sim.simulation_stopped:
        t = sim.getSimulationTime()
        while t == sim.getSimulationTime():
            simLoop(None, 0)

def sim_stop(sim):
    while sim.getSimulationState() != sim.simulation_stopped:
        sim.stopSimulation()
        simLoop(None, 0)


def sim_thread_func(app_dir, scene, num_timesteps=10e5, lock=None):
    if lock != None:
        lock.acquire() # only load new scene after previous completes (avoid overlap)

    import coppeliasim.bridge
    print(datetime.now(), "begin")
    simInitialize(c_char_p(app_dir.encode('utf-8')), 0)
    print(datetime.now(), "initialized")
    coppeliasim.bridge.load()

    print(datetime.now(), "loaded")

    # fetch CoppeliaSim API sim-namespace functions:
    global sim
    sim = coppeliasim.bridge.require('sim')
    v = sim.getInt32Param(sim.intparam_program_full_version)
    version = '.'.join(str(v // 100**(3-i) % 100) for i in range(4))
    print('CoppeliaSim version is:', version)

    print(datetime.now(), "sim aquired")

    sim.loadScene(scene)

    print(datetime.now(), "scene loaded")
    sim_start(sim)

    if lock != None:
        lock.release() # only load new scene after previous completes (avoid overlap)

    print(datetime.now(), "sim started")
    for i in range(int(num_instances)):
        t = sim.getSimulationTime()
        print(f'Simulation time: {t:.2f} [s] (simulation running synchronously to client, i.e. stepped)')
        sim_step(sim)
    sim_stop(sim)
    simDeinitialize()


def simThreadFunc(appDir):
    # example: simply run CoppeliaSim:
    while not simGetExitRequest():
        simLoop(None, 0)
    simDeinitialize()

def run_simulation(app_dir, sim_data):
        t = threading.Thread(target=thread_function, args=(app_dir, sim_data))
        t.start()
        simRunGui(options)
        t.join()


def get_options(headless):
    sim_gui_all = 0x0ffff
    sim_gui_headless = 0x10000

    if headless:
        return sim_gui_headless
    else:
        return sim_gui_all
    
def simulate(headless=True):
    options = get_options(headless)

def get_coppeliasim_library(lib_name, true_headless):
    # if 'default' is given, retrieve default library path
    if lib_name == 'default':
        defaultLibNameBase = 'coppeliaSim'
        if true_headless:
            defaultLibNameBase = 'coppeliaSimHeadless'
        from pathlib import Path
        # libPath = Path(__file__).absolute().parent
        libPath = "/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev10_Ubuntu20_04/"
        import platform
        plat = platform.system()
        if plat == 'Windows':
            libPath += defaultLibNameBase + '.dll'
        elif plat == 'Linux':
            libPath += 'lib' + defaultLibNameBase + '.so'
        elif plat == 'Darwin':
            libPath = libPath / '..' / 'MacOS' / 'lib' + defaultLibNameBase + '.dylib'
        
        return str(libPath)
    
    # if custom library specified, use it
    return lib_name

if __name__ == '__main__':
    sys.path.append(str(Path(__file__).absolute().parent / 'python'))
    sys.path.append("/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev10_Ubuntu20_04")
    import coppeliasim.cmdopt
    
    parser = argparse.ArgumentParser(description='CoppeliaSim client.', add_help=False)
    coppeliasim.cmdopt.add(parser)
    args = parser.parse_args()
    # if args.coppeliasim_library == 'default':
    #     defaultLibNameBase = 'coppeliaSim'
    #     if args.true_headless:
    #         defaultLibNameBase = 'coppeliaSimHeadless'
    #     from pathlib import Path
    #     # libPath = Path(__file__).absolute().parent
    #     libPath = "/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev10_Ubuntu20_04/"
    #     import platform
    #     plat = platform.system()
    #     if plat == 'Windows':
    #         libPath += defaultLibNameBase + '.dll'
    #     elif plat == 'Linux':
    #         libPath += 'lib' + defaultLibNameBase + '.so'
    #     elif plat == 'Darwin':
    #         libPath = libPath / '..' / 'MacOS' / 'lib' + defaultLibNameBase + '.dylib'
    #     args.coppeliasim_library = str(libPath)
    
    coppeliasim_library = get_coppeliasim_library(args.coppeliasim_library, args.true_headless)
    print("should be app dir:", coppeliasim_library)
    builtins.coppeliasim_library = coppeliasim_library
    from coppeliasim.lib import *

    options = coppeliasim.cmdopt.parse(args)
    # options = get_options(headless=True)
    print("lib:", coppeliasim_library, "type:", type(coppeliasim_library))
    app_dir = os.path.dirname(coppeliasim_library.encode('utf-8'))
    thread_function = sim_thread_func

    coppelia_path="/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev10_Ubuntu20_04/"
    scene = '/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev10_Ubuntu20_04/scenes/stickbug/05_Pole_Test_empty.ttt'
    gripper = 'models/stickbug/FingerClaw.ttm'

    lock = multiprocessing.Lock()

    sim_data = {
        'app_dir':app_dir,
        'scene':scene,
        'lock': lock,
    }


    if args.true_headless:
        thread_function(**sim_data)
    else:
        num_instances = 3
        child_process_list = []
        for i in range(num_instances):
            p = multiprocessing.Process(target=sim_thread_func, 
                                        kwargs=sim_data)
            p.start()
            child_process_list.append(p)
            
            
        for i in range(num_instances):
            p = child_process_list[i]
            p.join()
