from claw_test import *

def claw_test():
    scenario = {
        'headless': True,
        'scene': pole_scene_5cm,
        'claw': Finger_Flex,
        'actuator': {
            'name': 'VerticalForce',
            'force': {
                'starting_value': 0.1,
                'mode':'linear',
                'rate':1.0,
            },
            'wait_time': 5.0,
        },
    }

    run_scenario(startup_lock=None, **scenario)
