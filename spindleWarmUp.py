#################################################################################
#
# start spindle warmup
#
################################################################################# 
exec(open('functions.py', encoding='utf-8').read())
import time



#check machine in idle state
if d.getState() != State.Idle:
    print("Steuerung muß eingeschaltet sein.")
    exit(0)

#Definition countdown timer
def countdown(minutes):
    seconds = minutes * 60
    while seconds > 0:
        mins, secs = divmod(seconds, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        gui.edTimer.setText(timer)
        time.sleep(1)
        seconds -= 1

#Definition spindlewarmup process
def process(name, minutes):
    print(f"Warmlauf {name} U/min gestartet.")
    countdown(minutes)

total_time = warmuptime

# calculation of the warmuptime
rpm_step_time = total_time // 3

# main spindlewarmup process
d.setSpindleSpeed(rpm1)
d.setSpindleState(SpindleState.CW_ON)
process(rpm1, rpm_step_time)

d.setSpindleSpeed(rpm2)
d.setSpindleState(SpindleState.CW_ON)
process(rpm2, rpm_step_time)

d.setSpindleSpeed(rpm3)
d.setSpindleState(SpindleState.CW_ON)
process(rpm3, rpm_step_time)

#stop spindle
d.setSpindleState(SpindleState.OFF)
gui.edTimer.setText("")

print("Warmlauf beendet.")
