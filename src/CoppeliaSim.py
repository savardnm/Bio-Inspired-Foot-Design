import subprocess

path_to_compeliasim = "/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev10_Ubuntu20_04/coppeliaSim.sh"
flags = []

def execute():
    subprocess.run() 

def coppelia_sim(autoquit=True):
    command = path_to_coppeliasim

    if autoquit:
        flags.append("-q")


def add_