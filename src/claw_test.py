from coppelia import *
from batch_test import process_batch


coppelia_path="/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev10_Ubuntu20_04/"

pole_scene_5cm = 'scenes/stickbug/05_Pole_Test.ttt'
finger_claw = 'models/stickbug/FingerClaw.ttm'
hook_claw = 'models/stickbug/HookClaw.ttm'

def batch_claw_test(scenario_list):
    for scenario in scenario_list:
        pass
        

def sim_thread_func(app_dir, scene, num_timesteps=10e3, lock=None):
    if lock != None:
        lock.acquire()

    sim = setup_sim(app_dir)

    # example: load a scene, run the simulation for 1000 steps, then quit:
    sim.loadScene(scene)

    start_sim(sim)

    if lock != None:
        lock.release()

    for i in range(int(num_timesteps)):
        t = sim.getSimulationTime()
        print(f'Simulation time: {t:.2f} [s] (simulation running synchronously to client, i.e. stepped)')
        step_sim(sim)
    stop_sim(sim)


def main():
    claw_list = [finger_claw, hook_claw]
    scene_list = [pole_scene_5cm]
    actuator_list = ['VerticalForce', 'HorizontalForce']

    scenario_list = [{'scene':scene, 
                      'claw': claw, 
                      'actuator':actuator} 
                     for scene in scene_list 
                     for claw in claw_list 
                     for actuator in actuator_list]

    batch_claw_test(scenario_list)

if __name__ == '__main__':
    main()

