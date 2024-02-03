# Disclaimer: The provided code is open-source and free to use, modify, and distribute. 
# The author shall not be held responsible for any injury, damage, or loss resulting from the use of this code.
# By using this code, you agree to assume all responsibility and risk associated with the use of the code.
# Be careful anyway, this is not a safe way to change a tool, because the machine  is still "enable"

# If like me you have bought a Simcnc card but your change tool rack is not ready, you will need to change the tool manually.
# Replace the M6.py in the simcnc folder by thise one.


import time
import sys
import tkinter as tk
from tkinter import messagebox

# Parameters from the screen
toolChangePosX=float(d.getMachineParam(304))
toolChangePosY=float(d.getMachineParam(305))
toolLengthSensorPosX=float(d.getMachineParam(307))
toolLengthSensorPosY=float(d.getMachineParam(308))
probeIndexToolLength=int(d.getMachineParam(321))
ZtoolLengthMeasureFastProbeSpeed=float(d.getMachineParam(317))
ZtoolLengthMeasureSlowProbeSpeed=float(d.getMachineParam(318))

# where you want the spindel for the change of your tools
X_pos_change_tool = toolChangePosX
Y_pos_change_tool = toolChangePosY
Z_pos_change_tool = 0

# speed of move to reach the above position
vel = 3000

# Get the machine's position and name it "position".
pos = d.getPosition(CoordMode.Machine)

# name axis when d.getposition respond
X = 0
Y = 1
Z = 2

# Get the tool number from the gcode and name it "new tool".
new_tool = d.getSelectedToolNumber()

# Get the known size in simcnc of the new tool name it "new_tool_length"
new_tool_length = d.getToolLength(new_tool)

# Set in simcnc the tool infos
d.setToolLength (new_tool,new_tool_length)
d.setToolOffsetNumber(new_tool)
d.setSpindleToolNumber(new_tool)

# moving commande, call by Move_to_change_tool_pos() in the macro
def Move_to_change_tool_pos():
    # move Z 
    pos[Z] = Z_pos_change_tool
    d.moveToPosition(CoordMode.Machine, pos, vel)

    # move to change tool place
    pos[X] = X_pos_change_tool
    pos[Y] = Y_pos_change_tool
    d.moveToPosition(CoordMode.Machine, pos, vel)

# Create a message box with 3 buttons and execute probing.py or d.enableMachine(False)
def measurement():
    ###
    #Settings
    ###
    # probe index
    probeIndex = probeIndexToolLength
    # probing start position [X, Y, Z]
    probeStartAbsPos = [toolLengthSensorPosX, toolLengthSensorPosY, 0]
    # Axis Z probing end position (absolute)
    zEndPosition = -122
    # the absolute position of the Z axis of the probe contact for the reference tool
    refToolProbePos = -120.220
    # approach velocity (units/min)
    #vel = 15000
    # probing velocity (units/min)
    fastProbeVel = ZtoolLengthMeasureFastProbeSpeed
    slowProbeVel = ZtoolLengthMeasureSlowProbeSpeed
    # lift up dist before fine probing
    goUpDist = 5
    # delay (seconds) before fine probing
    fineProbingDelay = 0.2
    # other options
    moveX = True
    moveY = True
    checkFineProbingDiff = False
    fineProbeMaxAllowedDiff = 0.1

    ###
    #Measurement
    ###
    d.setSpindleState(SpindleState.OFF)
    toolNr = d.getSpindleToolNumber()
    if(toolNr == 0):
      sys.exit("Tool(0) has no tool lenght offset. Probing failed!")

    # get current absolute position
    pos = d.getPosition(CoordMode.Machine)

    # lift up Z to absolute 0
    pos[Axis.Z.value] = 0;
    d.moveToPosition(CoordMode.Machine, pos, vel)

    # go to XY start probe position
    if(moveX == True):
      pos[Axis.X.value] = probeStartAbsPos[Axis.X.value]
    if(moveY == True):
      pos[Axis.Y.value] = probeStartAbsPos[Axis.Y.value]
    d.moveToPosition(CoordMode.Machine, pos, vel)

    # go to Z start probe position
    pos[Axis.Z.value] = probeStartAbsPos[Axis.Z.value]
    d.moveToPosition(CoordMode.Machine, pos, vel)

    # start fast probing
    pos[Axis.Z.value] = zEndPosition;
    probeResult = d.executeProbing(CoordMode.Machine, pos, probeIndex, fastProbeVel)
    if(probeResult == False):
      sys.exit("fast probing failed!")
  
    # get fast probe contact position
    fastProbeFinishPos = d.getProbingPosition(CoordMode.Machine)

    # lift-up Z
    d.moveAxisIncremental(Axis.Z, goUpDist, vel)
    # delay
    time.sleep(fineProbingDelay)
    # start fine probing
    probeResult = d.executeProbing(CoordMode.Machine, pos, probeIndex, slowProbeVel)
    if(probeResult == False):
      sys.exit("slow probing failed!")
  
    # get fine probe contact position
    probeFinishPos = d.getProbingPosition(CoordMode.Machine)

    # check diff between fast and fine probing
    probeDiff = abs(fastProbeFinishPos[Axis.Z.value] - probeFinishPos[Axis.Z.value])
    if(probeDiff > fineProbeMaxAllowedDiff and checkFineProbingDiff == True):
      errMsg = "ERROR: fine probing difference limit exceeded! (diff: {:.3f})".format(probeDiff)
      sys.exit( errMsg)

    # calculate and set tool length
    toolOffset = probeFinishPos[Axis.Z.value] - refToolProbePos
    d.setToolLength(toolNr, toolOffset)

    # lift Z to abs 0
    pos[Axis.Z.value] = 0
    d.moveToPosition(CoordMode.Machine, pos, vel)

    # finish
    print("Werkzeug Nr.:{:d} hat Werkzeuglänge: {:.4f}").format(toolNr, toolOffset)
    root.destroy()
    
    
    
def stop():
    d.stopTrajectory()
    root.destroy()
    print("Programm wurde beendet.")

def toggle_blink():
    if message_label.cget("foreground") == "black":
        message_label.config(fg="red")
    else:
        message_label.config(fg="black")
    root.after(500, toggle_blink)  # Toggle every 500 milliseconds

def show_custom_message_box():
    global root, message_label

    root = tk.Tk()
    root.title("M6 Werkzeugwechsel")
    root.geometry("700x300+{}+{}".format(int(root.winfo_screenwidth()/2 - 350), int(root.winfo_screenheight()/2 - 150)))
    root.minsize(width=680, height=280)
    root.maxsize(width=750, height=350)
    
    custom_font = ('Helvetica', 12)  # Define a custom font 

    message_label = tk.Label(root, text="!!!G-Code M6 Werkzeugwechsel!!! \n\nBitte Fräser Nummer #"  + str(new_tool) + " einsetzten. \n\nDanach wählen Sie aus wie sie fortfahren möchten.", font=custom_font)
    message_label.pack(padx=50, pady=50)

    toggle_blink()  # Start blinking

    # Make the window always on top
    root.wm_attributes("-topmost", 1)

    
    def on_closing():
        d.enableMachine(False)  # Disable the machine if the X button is clicked
        root.destroy()  # close messagebox

    button_frame = tk.Frame(root)
    button_frame.pack()

    continuer_button = tk.Button(button_frame, text="\u25B6 Ohne Messen fortsetzen ", command=root.destroy, font=custom_font)
    continuer_button.pack(side=tk.LEFT, padx=30, pady=30)

    measurement_button = tk.Button(button_frame, text="Werkzeug vermessen", command=measurement, font=custom_font)
    measurement_button.pack(side=tk.LEFT, padx=30, pady=30)

    stop_button = tk.Button(button_frame, text="\u25A0 STOP", command=stop, fg="white", bg="red", font=custom_font)
    stop_button.pack(side=tk.RIGHT, padx=30, pady=30)

    # Captures the window close event
    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()

########################################################
# macro start
########################################################
#print ("Manual change tool Start")

#Turn off the spindle
d.setSpindleState(SpindleState.OFF) 

# if new tool length = zero, execute Move_to_change_tool_pos
if new_tool_length == 0:  
    Move_to_change_tool_pos()

#call the message box display function
show_custom_message_box()

#print ("Manual change tool finish")