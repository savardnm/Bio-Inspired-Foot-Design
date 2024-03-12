#python


def sysCall_init():
    self.sim = require('sim')
    self.prev_unit_spring = None

    print("initialized Louse Claw Spring 0")

    # do some initialization here
    #
    # Instead of using globals, you can do e.g.:
    # self.myVariable = 21000000

def set_prev_unit_spring(_prev_unit_spring):
    self.prev_unit_spring = _prev_unit_spring

def sysCall_actuation():
    if self.prev_unit_spring == None:
        return
    
    object_handle = self.sim.getObject(".")

    own_position = self.sim.getJointPosition(object_handle)
    prev_position = self.sim.getJointPosition(self.prev_unit_spring)

    max_offset = 0.05

    offset = own_position - prev_position

    if offset > max_offset:
        self.sim.setJointPosition(object_handle, prev_position + max_offset)


def sysCall_sensing():
    # put your sensing code here
    pass

def sysCall_cleanup():
    # do some clean-up here
    print("CLEANUP Louse Claw Spring 0")
    pass

# See the user manual or the available code snippets for additional callback functions and details
