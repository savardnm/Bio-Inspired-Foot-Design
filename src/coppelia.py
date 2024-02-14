# need to set DYLD_LIBRARY_PATH=$PWD/../Frameworks
# to avoid libraries load errors

import argparse
import os
import sys
import threading
from time import sleep

from pathlib import Path
from ctypes import *

copp_lib_dir = "/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev10_Ubuntu20_04/"
sys.path.append(copp_lib_dir)

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

        coppeliasim_library = get_library(true_headless=true_headless)
        from coppeliasim.lib import simRunGui
        self.run_gui = simRunGui

        # TODO: Bug: Cannot use true headless >:(
        self.options = get_gui_options(headless=headless, true_headless=true_headless)

        self.app_dir = os.path.dirname(coppeliasim_library)

        self.call_stack = []
        self.lock = threading.Lock()

        if self.true_headless:
            self.sim_thread_func()
        else:
            # self.sim_setup_thread = threading.Thread(target=self.setup_sim)
            self.gui_thread = threading.Thread(target=self.run_gui, args=(self.options,))
            self.gui_thread.start()
            self.setup_sim()
            # self.sim_setup_thread.join()
    
    def start(self):
        if self.is_stopped():
            self.api.startSimulation()

    def is_stopped(self):
        return self.api.getSimulationState() == self.api.simulation_stopped
        
    def spin(self):
        self.loop(None, 0)

    def step(self):
        if self.api.getSimulationState() != self.api.simulation_stopped:
            t = self.api.getSimulationTime()
            while t == self.api.getSimulationTime():
                self.loop(None, 0)

    def stop(self):
        while self.api.getSimulationState() != self.api.simulation_stopped:
            self.api.stopSimulation()
            self.loop(None, 0)

    def close(self):
        self.deinitialize()
        self.gui_thread.join()


    def setup_sim(self):
        from coppeliasim.lib import simInitialize, simDeinitialize, simLoop, simGetExitRequest

        self.initialize = simInitialize
        self.deinitialize = simDeinitialize
        self.loop = simLoop
        self.get_exit_request = simGetExitRequest

        import coppeliasim.bridge
        simInitialize(c_char_p(self.app_dir.encode('utf-8')), 0)
        coppeliasim.bridge.load()

        # fetch CoppeliaSim API sim-namespace functions:
        self.api = coppeliasim.bridge.require('sim')

        v = self.api.getInt32Param(self.api.intparam_program_full_version)
        version = '.'.join(str(v // 100**(3-i) % 100) for i in range(4))
        print('CoppeliaSim version is:', version)
        # i = 0
        # while(True):
        #     if i % 2:
        #         sym = '.'
        #     else:
        #         sym = ' '
        #     print("Running " + "".join([sym] * (i % 10)), end="\r")
        #     i += 1
        #     self.lock.acquire()
        #     if len(self.call_stack) != 0:
        #         call = self.call_stack.pop()
        #         self.call(**call)
        #         print("calling", call, end="\r")
        #     self.lock.release()
        #     sleep(0.01)
        
    def load_scene(self, scene):
        self.api.loadScene(scene)

    def request_call(self, **kwargs):
        print("awaiting lock")
        self.lock.acquire()
        self.call_stack.append(kwargs)
        self.lock.release()

    def call(self, function, args=[], kwargs={}):
        function(*args, **kwargs)

def run_basic(sim):
    # example: simply run CoppeliaSim:
    while not sim.get_exit_request():
        sim.loop(None, 0)
    sim.deinitialize()
    sim.gui_thread.join()

def run_scene(sim, scene):
    sim.load_scene(scene)
    sim.start()
    for i in range(1000):
        t = sim.api.getSimulationTime()
        print(f'Simulation time: {t:.2f} [s] (simulation running synchronously to client, i.e. stepped)')
        sim.step()
    sim.stop()
    sim.deinitialize()

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
    run_scene(sim, pole_scene)