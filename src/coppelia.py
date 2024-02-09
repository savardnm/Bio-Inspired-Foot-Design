# need to set DYLD_LIBRARY_PATH=$PWD/../Frameworks
# to avoid libraries load errors

import argparse
import os
import sys
import threading

from pathlib import Path
from ctypes import *

copp_lib_dir = "/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev10_Ubuntu20_04/"

def simStart():
    if sim.getSimulationState() == sim.simulation_stopped:
        sim.startSimulation()

def simStep(simLoop):
    if sim.getSimulationState() != sim.simulation_stopped:
        t = sim.getSimulationTime()
        while t == sim.getSimulationTime():
            simLoop(None, 0)

def simStop(simLoop):
    while sim.getSimulationState() != sim.simulation_stopped:
        sim.stopSimulation()
        simLoop(None, 0)

def simThreadFunc(app_dir, scene, lock=None):
    if lock != None:
        lock.acquire()
        
    from coppeliasim.lib import simInitialize, simDeinitialize, simLoop
    import coppeliasim.bridge
    simInitialize(c_char_p(app_dir.encode('utf-8')), 0)
    coppeliasim.bridge.load()

    # fetch CoppeliaSim API sim-namespace functions:
    global sim
    sim = coppeliasim.bridge.require('sim')

    v = sim.getInt32Param(sim.intparam_program_full_version)
    version = '.'.join(str(v // 100**(3-i) % 100) for i in range(4))
    print('CoppeliaSim version is:', version)

    # example: load a scene, run the simulation for 1000 steps, then quit:
    sim.loadScene(scene)
    simStart()

    if lock != None:
        lock.release()

    for i in range(10000):
        t = sim.getSimulationTime()
        print(f'Simulation time: {t:.2f} [s] (simulation running synchronously to client, i.e. stepped)')
        simStep(simLoop)
    simStop(simLoop)
    simDeinitialize()

def get_gui_options(headless, true_headless):
    sim_gui_all = 0x0ffff
    sim_gui_headless = 0x10000

    if headless or true_headless:
        options = sim_gui_headless
    else:
        options = sim_gui_all
    
    return options

def simulate(headless=False, true_headless=False, **kwargs):
    coppeliasim_library = get_library(true_headless=False)
    
    sys.path.append(copp_lib_dir)
    from coppeliasim.lib import simRunGui

    # TODO: Bug: Cannot use true headless >:(
    options = get_gui_options(headless=headless, true_headless=true_headless)

    appDir = os.path.dirname(coppeliasim_library)

    if true_headless:
        simThreadFunc(appDir, **kwargs)
    else:
        t = threading.Thread(target=simThreadFunc, args=(appDir,), kwargs=kwargs)
        t.start()
        simRunGui(options)
        t.join()

def get_library(true_headless=False):
    defaultLibNameBase = 'coppeliaSim'
    if true_headless:
        defaultLibNameBase = 'coppeliaSimHeadless'
    from pathlib import Path
    libPath = Path(copp_lib_dir)

    import platform
    plat = platform.system()
    if plat == 'Windows':
        libPath /= defaultLibNameBase + '.dll'
    elif plat == 'Linux':
        libPath /= 'lib' + defaultLibNameBase + '.so'
    elif plat == 'Darwin':
        libPath = libPath / '..' / 'MacOS' / 'lib' + defaultLibNameBase + '.dylib'
    coppeliasim_library = str(libPath)

    import builtins
    builtins.coppeliasim_library = coppeliasim_library

    return coppeliasim_library

if __name__ == '__main__':
    pole_scene = '/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev10_Ubuntu20_04/scenes/stickbug/05_Pole_Test.ttt'
    simulate(scene=pole_scene, headless=True)