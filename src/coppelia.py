# need to set DYLD_LIBRARY_PATH=$PWD/../Frameworks
# to avoid libraries load errors

import argparse
import os
import sys
import threading

from pathlib import Path
from ctypes import *

copp_lib_dir = "/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev10_Ubuntu20_04/"
sys.path.append(copp_lib_dir)

def setup_sim(app_dir):
    from coppeliasim.lib import simInitialize, simDeinitialize, simLoop
    sim = {
        "initialize": simInitialize,
        "deinitialize": simDeinitialize,
        "loop": simLoop
    }

    import coppeliasim.bridge
    simInitialize(c_char_p(app_dir.encode('utf-8')), 0)
    coppeliasim.bridge.load()

    # fetch CoppeliaSim API sim-namespace functions:
    sim['api'] = coppeliasim.bridge.require('sim')

    v = sim['api'].getInt32Param(sim['api'].intparam_program_full_version)
    version = '.'.join(str(v // 100**(3-i) % 100) for i in range(4))
    print('CoppeliaSim version is:', version)
    return sim

def start_sim(api, *args, **kwargs):
    if api.getSimulationState() == api.simulation_stopped:
        api.startSimulation()

def step_sim(api, loop, *args, **kwargs):
    if api.getSimulationState() != api.simulation_stopped:
        t = api.getSimulationTime()
        while t == api.getSimulationTime():
            loop(None, 0)

def stop_sim(api, loop, *args, **kwargs):
    while api.getSimulationState() != api.simulation_stopped:
        api.stopSimulation()
        loop(None, 0)

def close_sim(deinitialize, *args, **kwargs):
    deinitialize()

def simThreadFunc(app_dir, sim_args, scene, num_timesteps=5e3, lock=None):
    if lock != None:
        lock.acquire()

    # sim_args = setup_sim(app_dir)
    sim_api = sim_args['api']

    # example: load a scene, run the simulation for 1000 steps, then quit:
    sim_api.loadScene(scene)

    start_sim(**sim_args)

    if lock != None:
        lock.release()

    for i in range(int(num_timesteps)):
        t = sim_api.getSimulationTime()
        print(f'Simulation time: {t:.2f} [s] (simulation running synchronously to client, i.e. stepped)')
        step_sim(**sim_args)
    stop_sim(**sim_args)
    close_sim(**sim_args)

def get_gui_options(headless, true_headless):
    sim_gui_all = 0x0ffff
    sim_gui_headless = 0x10000

    if headless or true_headless:
        options = sim_gui_headless
    else:
        options = sim_gui_all
    
    return options

class Sim:
    def __init__(self, headless, true_headless=False) -> None:
        self.headless = headless
        self.true_headless = true_headless

        coppeliasim_library = get_library(true_headless=False)
        from coppeliasim.lib import simRunGui
        self.run_gui = simRunGui

        # TODO: Bug: Cannot use true headless >:(
        self.options = get_gui_options(headless=headless, true_headless=true_headless)

        self.appDir = os.path.dirname(coppeliasim_library)

        self.sim_args = setup_sim()
        

    def setup_sim(self):
        from coppeliasim.lib import simInitialize, simDeinitialize, simLoop
        sim = {
            "initialize": simInitialize,
            "deinitialize": simDeinitialize,
            "loop": simLoop
        }

        import coppeliasim.bridge
        simInitialize(c_char_p(self.appDir.encode('utf-8')), 0)
        coppeliasim.bridge.load()

        # fetch CoppeliaSim API sim-namespace functions:
        sim['api'] = coppeliasim.bridge.require('sim')

        v = sim['api'].getInt32Param(sim['api'].intparam_program_full_version)
        version = '.'.join(str(v // 100**(3-i) % 100) for i in range(4))
        print('CoppeliaSim version is:', version)
        return sim


    def simulate(self, **kwargs):
        if self.true_headless:
            simThreadFunc(self.appDir, **kwargs)
        else:
            t = threading.Thread(target=simThreadFunc, args=(self.appDir,), kwargs=kwargs)
            t.start()
            self.run_gui(self.options)
            t.join()


def simulate(headless=False, true_headless=False, **kwargs):
    coppeliasim_library = get_library(true_headless=False)
    
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
    # simulate(scene=pole_scene, headless=True)
    sim = Sim(headless=False)
    sim.simulate(scene=pole_scene, sim_args=sim.sim_args)