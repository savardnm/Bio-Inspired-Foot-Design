-- Command Line:
-- ./coppeliaSim.sh -q -h -s500000 -gmodels/stickbug/FingerClaw.ttm -g10 -g0 scenes/stickbug/05_Pole_Test_detached.ttt
sim = require('sim')
sim.setThreadAutomaticSwitch(true)
sim.switchThread()

local objectHandle  -- Define objectHandle as a global variable
local force_value
local growth_factor = 1.05
local position_threshold = 0.1
local final_force
local milestone=10
local default_force = 10

function sysCall_init()
    local scriptHandle = sim.handle_self
    objectHandle = sim.getObjectAssociatedWithScript(scriptHandle)

    force_value = sim.getStringParameter(sim.stringparam_app_arg2)
    force_value = tonumber(force_value)
end

function sysCall_actuation()

    if force_value == nil then
        force_value = default_force
    end

    if force_value ~= nil then
        control_loop(force_value)
    end
end

function control_loop(input_force_value)
    local simulationTime = sim.getSimulationTime()
    position_value = sim.getJointPosition(objectHandle)

    local growth = growth_factor ^ simulationTime
    local force = input_force_value * growth

    if simulationTime < 1.0 then
        force=0.0
    end

    if position_value < position_threshold then
        print("stopping")
        sim.stopSimulation()
    end

    final_force = force

    if math.abs(force) > milestone then
        print("V: F:", string.format("%.2f", final_force), "\tPos:", string.format("%.2f", position_value), "\tT:", simulationTime)
        milestone = milestone * 2
    end
    
    sim.setJointForce(objectHandle, final_force)

end



function sysCall_sensing()
    -- put your sensing code here
end

function sysCall_cleanup()
    print("Final Vertical Force:", final_force)
    -- do some clean-up here
end
