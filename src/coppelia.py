import builtins
import os
import threading
import sys

from ctypes import *

# set the path to the coppeliaSim's library:

coppeliasim_dir = "/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev10_Ubuntu20_04/"
builtins.coppeliasim_library = coppeliasim_dir + "libcoppeliaSim.so"

sys.path.append(coppeliasim_dir)

# import the coppeliaSim's library functions:
from coppeliasim.lib import *

appDir = os.path.dirname(builtins.coppeliasim_library)

def simThreadFunc(appDir):
    simInitialize(c_char_p(appDir.encode('utf-8')), 0)
    while not simGetExitRequest():
        simLoop(None, 0)
    simDeinitialize()

if __name__ == "__main__":
    trueHeadless=False
    headless=False

    sim_gui_all = 0x0ffff
    sim_gui_headless = 0x10000
    
    # start the sim thread (see in the next section)
    if trueHeadless:
        simThreadFunc(appDir)
    else:
        t = threading.Thread(target=simThreadFunc, args=(appDir,))
        t.start()
        simRunGui(sim_gui_all) # use sim_gui_headless for headless mode
        t.join()