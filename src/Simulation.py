# need to set DYLD_LIBRARY_PATH=$PWD/../Frameworks
# to avoid libraries load errors

import argparse
import builtins
import os
import sys
import threading

from pathlib import Path
from ctypes import *

copp_lib_dir = "/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev10_Ubuntu20_04/"
sys.path.append(copp_lib_dir)

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

    pole_scene = '/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev10_Ubuntu20_04/scenes/stickbug/05_Pole_Test.ttt'
    sim.loadScene(pole_scene)
    simStart()
    for i in range(500):
        t = sim.getSimulationTime()
        print(f'Simulation time: {t:.2f} [s] (simulation running synchronously to client, i.e. stepped)')
        simStep()
    simStop()
    simDeinitialize()

class Sim:
    def __init__(self) -> None:
        pass

if __name__ == '__main__':
    import coppeliasim.cmdopt
    parser = argparse.ArgumentParser(description='CoppeliaSim client.', add_help=False)
    coppeliasim.cmdopt.add(parser)
    args = parser.parse_args()
    if args.coppeliasim_library == 'default':
        defaultLibNameBase = 'coppeliaSim'
        if args.true_headless:
            defaultLibNameBase = 'coppeliaSimHeadless'
        from pathlib import Path
        # libPath = Path(__file__).absolute().parent
        libPath = Path(copp_lib_dir)
        import platform
        plat = platform.system()
        if plat == 'Windows':
            libPath /= defaultLibNameBase + '.dll'
        elif plat == 'Linux':
            libPath /= 'lib' + defaultLibNameBase + '.so'
        elif plat == 'Darwin':
            libPath = libPath / '..' / 'MacOS' / 'lib' + defaultLibNameBase + '.dylib'
        args.coppeliasim_library = str(libPath)
    
    builtins.coppeliasim_library = args.coppeliasim_library
    from coppeliasim.lib import *

    options = coppeliasim.cmdopt.parse(args)

    appDir = os.path.dirname(args.coppeliasim_library)

    if args.true_headless:
        simThreadFunc(appDir)
    else:
        t = threading.Thread(target=simThreadFunc, args=(appDir,))
        t.start()
        simRunGui(options)
        t.join()
