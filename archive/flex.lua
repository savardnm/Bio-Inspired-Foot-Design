-- lua
local default_gripper_model_path = "/home/nathan/Programs/CoppeliaSim/CoppeliaSim_Edu_V4_6_0_rev10_Ubuntu20_04/models/stickbug/FingerClaw.ttm"
local gripper_model
local objectHandle

function sysCall_init()
    sim = require('sim')

    local scriptHandle = sim.handle_self
    objectHandle = sim.getObjectAssociatedWithScript(scriptHandle)

    local path_to_gripper = get_model_path()

    load_attach_gripper(path_to_gripper)


    -- do some initialization here
end

function load_attach_gripper(path_to_gripper)
    print("loading gripper model: ", path_to_gripper)
    gripper_model = sim.loadModel(path_to_gripper)
    local self_location = sim.getObjectPosition(objectHandle)
    local offset = {0,0.05,0}
    sim.setObjectPosition(gripper_model, add_mat(self_location, offset))
    sim.setObjectParent(gripper_model, objectHandle, true)

end

function get_model_path()
    local path = sim.getStringParameter(sim.stringparam_app_arg1)
    
    if path == "" then
        path = default_gripper_model_path
    end
    
    return path
end

function add_mat(a, b)
    c = {}
    if #a==#b then
        for i=1,#a do
         c[i]=a[i]+b[i]
        end
    end

    return c
        
end

function sysCall_actuation()
    -- put your actuation code here
end

function sysCall_sensing()
    -- put your sensing code here
end

function sysCall_cleanup()
    -- do some clean-up here
end

-- See the user manual or the available code snippets for additional callback functions and details
