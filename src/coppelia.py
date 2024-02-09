# need to set DYLD_LIBRARY_PATH=$PWD/../Frameworks
# to avoid libraries load errors

import argparse
import builtins
import os
import sys
import threading

from pathlib import Path
from ctypes import *


def simStart():
    if sim.getSimulationState() == sim.simulation_stopped:
        sim.startSimulation()

def simStep():
    if sim.getSimulationState() != sim.simulation_stopped:
        t = sim.getSimulationTime()
        while t == sim.getSimulationTime():
            simLoop(None, 0)

def simStop():
    while sim.getSimulationState() != sim.simulation_stopped:
        sim.stopSimulation()
        simLoop(None, 0)

def simThreadFunc(appDir):
    import coppeliasim.bridge

    simInitialize(c_char_p(appDir.encode('utf-8')), 0)

    coppeliasim.bridge.load()

    # fetch CoppeliaSim API sim-namespace functions:
    global sim
    sim = coppeliasim.bridge.require('sim')

    v = sim.getInt32Param(sim.intparam_program_full_version)
    version = '.'.join(str(v // 100**(3-i) % 100) for i in range(4))
    print('CoppeliaSim version is:', version)

    # example: load a scene, run the simulation for 1000 steps, then quit:
    sim.loadScene('/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev10_Ubuntu20_04/scenes/stickbug/05_Pole_Test.ttt')
    simStart()
    for i in range(10000):
        t = sim.getSimulationTime()
        print(f'Simulation time: {t:.2f} [s] (simulation running synchronously to client, i.e. stepped)')
        simStep()
    simStop()
    simDeinitialize()

    # # example: simply run CoppeliaSim:
    # while not simGetExitRequest():
    #     simLoop(None, 0)
    # simDeinitialize()

if __name__ == '__main__':
    copp_lib_dir = "/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev10_Ubuntu20_04/"
    sys.path.append(copp_lib_dir)
    # import coppeliasim.cmdopt
    # parser = argparse.ArgumentParser(description='CoppeliaSim client.', add_help=False)
    # coppeliasim.cmdopt.add(parser)
    # args = parser.parse_args()
    # if args.coppeliasim_library == 'default':
    #     defaultLibNameBase = 'coppeliaSim'
    #     if args.true_headless:
    #         defaultLibNameBase = 'coppeliaSimHeadless'
    #     from pathlib import Path
    #     # libPath = Path(__file__).absolute().parent
    #     libPath = copp_lib_dir
    #     import platform
    #     plat = platform.system()
    #     if plat == 'Windows':
    #         libPath += defaultLibNameBase + '.dll'
    #     elif plat == 'Linux':
    #         libPath += 'lib' + defaultLibNameBase + '.so'
    #     elif plat == 'Darwin':
    #         libPath = libPath / '..' / 'MacOS' / 'lib' + defaultLibNameBase + '.dylib'
    #     args.coppeliasim_library = str(libPath)
    true_headless = False
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
    
    builtins.coppeliasim_library = coppeliasim_library
    from coppeliasim.lib import *

    headless = False
    sim_gui_all = 0x0ffff
    sim_gui_headless = 0x10000
    if headless or true_headless:
        options = sim_gui_headless
    else:
        options = sim_gui_all
    # options = coppeliasim.cmdopt.parse(args)

    appDir = os.path.dirname(coppeliasim_library)

    if true_headless:
        simThreadFunc(appDir)
    else:
        t = threading.Thread(target=simThreadFunc, args=(appDir,))
        t.start()
        simRunGui(options)
        t.join()
