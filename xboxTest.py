##########################################
##              xboxTest.py             ##
##########################################
## Test the new xbox.py class           ##
##                                      ##
## Author: Connor Billings              ##
##########################################

###################
## configuration ##
###################

## imports
## These are external files that the robot requires to run properly.
import xboxNew
import time

## Instantiations
j = xboxNew.Joystick() ## new joystick



###########################################################
##                     MAINE LOOP                        ##
###########################################################
## The whole program takes place inside a while loop.    ##
## This loop runs continuously searching for user input. ##
###########################################################
try:
    print "This program tests the new Xbox controller."
    print "Press any button to see its output."
    while True:

        ## Buttons
        if j.whenA():
            print "when A"
        if j.whenB():
            print "when B"
        if j.whenX():
            print "when X"
        if j.whenY():
            print "when Y"
        if j.whenLeftTrigger():
            print "when LeftTrigger"
        if j.whenRightTrigger():
            print "when RightTrigger"
        if j.whenLeftThumbstick():
            print "when LeftThumbstick"
        if j.whenRightThumbstick():
            print "when RightThumbstick"
        if j.whenLeftBumper():
            print "when LeftBumper"
        if j.whenRightBumper():
            print "when RightBumper"
        if j.whenDpadUp():
            print "when Dpad Up"
        if j.whenDpadDown():
            print "when Dpad Down"
        if j.whenDpadLeft():
            print "when Dpad Left"
        if j.whenDpadRight():
            print "when Dpad Right"
        if j.whenRightJoystickUp():
            print "when RightJoystick Up"
        if j.whenRightJoystickDown():
            print "when RightJoystick Down"
        if j.whenRightJoystickLeft():
            print "when RightJoystick Left"
        if j.whenRightJoystickRight():
            print "when RightJoystick Right"
        
        
        
        time.sleep(0.033)

#############################################
## Turn-off configurations on program exit ##
#############################################
except:
    raise


