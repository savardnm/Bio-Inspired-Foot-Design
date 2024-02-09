from coppelia import simulate
from batch_test import process_batch


coppelia_path="/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev10_Ubuntu20_04/"

pole_scene_5cm = 'scenes/stickbug/05_Pole_Test.ttt'
finger_claw = 'models/stickbug/FingerClaw.ttm'
hook_claw = 'models/stickbug/HookClaw.ttm'

def batch_claw_test(scenario_list):
    for scenario in scenario_list:
        pass
        


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

