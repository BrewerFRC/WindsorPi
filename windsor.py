##########################################
##          windsorTest.py              ##
##########################################
## Test Version                         ##
## A Raspberry Pi version of Windsor    ##
## A 2016 competition robot built by    ##
## Team Orange Chaos (4564)             ##
##                                      ##
## Author: Connor Billings              ##
## Published: June 15, 2017             ##
## Updated: July 13, 2017               ##
##########################################

###################
## configuration ##
###################

## imports
## These are external files that the robot requires to run properly.
import drive
import maestro
import xbox
import time

#Relay controlled by raspberry pi 

import RPi.GPIO as io

## Constants
## These values are written as constants so that they can be changed
## here instead of having to re-write entire sections of code.

## Maestro Ports
LEFT_MOTORS = 0
RIGHT_MOTORS = 1
THROWER = 5
INTAKE = 6
ARM_INTAKE = 7
ARM = 4 ## Lower values = down,higher = up ; Stop at 1425

## RaspberryPi Ports
NERF_CANNONS = 4

"""
Note: Arm limits normally at 255 and go to 0 when pressed.
Thrower limit at 0 and goes to 255 when pressed.
"""
## Limit switches
THROWER_LIMIT = 11 ## TBD
ARM_LOWER_LIMIT = 9 ## TBD
ARM_UPPER_LIMIT = 10 ## TBD


## Motor On/Off Values
## Talon: 950 - 2050 (3800 - 8200)

THROWER_MAX = 8200
THROWER_MIN = 7400
THROWER_INC = 200
INTAKE_FWD = 8200  
INTAKE_REV_SLOW = 5500 
INTAKE_REV = 3800 
ARM_INTAKE_FWD = 8200 
ARM_INTAKE_REV = 3800
ARM_DOWN = 4800
ARM_UP = 6200
ARM_STOP = 5700 ## Use this to hold the arm stationary.
CANNONS_ON = 6000
CANNONS_OFF = 3800 ## Relay normally closed.  Add power to turn off.
MOTOR_OFF = 6000 ## This value will stop any motor controlled by the maestro.

## Variables
throwCounter = 0 ## Timer to control a throw.
offCounter = 0   ## Used to shut off everything by button press.
spinCounter = 0  ## Control how long the thrower spins back.
throwSpeed = THROWER_MAX ## Set speed of thrower. Default = 100%

## control booleans
isStarted = False 	## This disables all functionality until user presses start.
intakeEnabled = False 	## This determines whether or not the intake should run.
intakeHasBall = False   ## Determines if the intake is holding a ball.
rolledBack = False      ## Determines if the ball has been rolled back in the thrower.
throwerConfig = False	## Enter the section of code that configures the thrower.
throwerOn = False 	## This tells the motor if the thrower is on.
driveDisable = False 	## This controls the driving mode.
slowDriveMode = False	## Slow drive mode.
ArmDisabled = False	## Cut power to arm motor.
pressedB = False 	## Used to apply actions to falling edge of B button.
throwInProgress = False ## State that a throw in in progress.
throwSpeedLock = False  ## Lock thrower speed in place.

## Instantiations
j = xbox.Joystick() ## new joystick
motors = maestro.Controller() ## new maestro
dt = drive.DriveTrain(motors, LEFT_MOTORS, RIGHT_MOTORS) ## new drive train
io.setmode(io.BCM)
io.setup(NERF_CANNONS, io.OUT)
io.output(NERF_CANNONS, True) #Stop Cannons


###########################################################
##                     MAINE LOOP                        ##
###########################################################
## The whole program takes place inside a while loop.    ##
## This loop runs continuously searching for user input. ##
###########################################################
try:
    print "Robot on!"
    print "Press Start to enable."
    while True:

        ## All of these commands can only be run if the user has acknowleged
	## starting the robot and if the controller is connected.
        if isStarted and j.connected(): 
	    
            ####################
            ## Drive Controls ##
            ####################
            
            ## Driving
            ## Control: Left Joystick
            if not driveDisable:
                if not slowDriveMode:
                    ## Normal Drive Mode
                    ## Robot will respond only if joystick is more than 20% pressed to avoid accidental activation.
                    if abs(j.leftX()) <= .10 and abs(j.leftY()) <= .10:
                        dt.drive(0, 0) ## Don't drive.
                    else:
                        dt.drive(j.leftX() * 0.5, j.leftY()) ## Drive at 100% power. Turn at 100% power.
                        #print "Driving at full power."
                else:
                    ## Slow Drive Mode
		    ## Robot will respond only if joystick is more than 20% pressed to avoid accidental activation.
                    if abs(j.leftX()) <= .10 and abs(j.leftY()) <= .10:
                        dt.drive(0, 0) ## Don't drive.
                    else:
                        dt.drive(j.leftX() * .35, j.leftY() * .5) ## Drive at 50% power. Turn at 50% power.
                        #print "Driving in slow mode."
            else:
                dt.drive(0,0) ## Stop driving.

            ## Disable & Re-enable Driving
            ## Control: Back & Start
            if j.Back():
		dt.drive(0,0) ## Stop driving.
                driveDisable = True
                offCounter = offCounter + 1 ## Shut down if counter reaches 100
                if offCounter == 50:
                    isStarted = False
                    offCounter = 0
		#print "Driving Disabled"
            elif j.Start():
                driveDisable = False
		#print "Driving Enabled"
            else:
                offCounter = 0

            ## Fast/Slow Driving Mode
            ## Control: Dpad Up/Down
            if j.dpadDown():
                slowDriveMode = True
		#print "Slow Drive Mode"
            if j.dpadUp():
                slowDriveMode = False
		#print "Standard Drive Mode"
            		
            ###################
            ## arm & thrower ##
            ###################

            ## Lower/Raise Arm
            ## Control: Left/Right Bumper
            if not ArmDisabled:
                if j.leftBumper() and (not j.rightBumper()) and (motors.getDIO(ARM_LOWER_LIMIT)):    ## Respond to Left Bumper if the lower limit switch isn't pressed.
                    motors.setTarget(ARM, ARM_DOWN) 				    ## lower arm
                    #print "Lower Arm"
                elif j.rightBumper() and (not j.leftBumper()) and (motors.getDIO(ARM_UPPER_LIMIT)):  ## Respond to Right Bumper if the upper limit switch isn't pressed.
                    motors.setTarget(ARM, ARM_UP) 					    ## raise arm
                    #print "Raise Arm"
                else: 								    ## No bumper pressed or either limit switch pressed
                    motors.setTarget(ARM, ARM_STOP) 					    ## stop arm
            else:
                motors.setTarget(ARM, MOTOR_OFF)

				
	    ## Cut power to arm in case of motor overheating.
	    ## Control: Dpad left to lock, Dpad right to unlock.
	    if j.whenDpadLeft():
                ArmDisabled = True
            if j.whenDpadRight():
                ArmDisabled = False

                
            ## Start Intake
            ## Called at the start of thrower process
            ## Control: Y
            if j.whenY() and (not intakeHasBall) and (not motors.getDIO(THROWER_LIMIT)) and (not throwInProgress):
                intakeEnabled = not intakeEnabled
			
	    ## Run intake until limit switch activated or Y button pressed again.
            if intakeEnabled:
		if (motors.getDIO(THROWER_LIMIT)) and (not throwerOn):
		    motors.setTarget(INTAKE, MOTOR_OFF)	    ## Turn off inner intake.
		    motors.setTarget(ARM_INTAKE, MOTOR_OFF) ## Turn off arm intake.
                    intakeHasBall = True
		    intakeEnabled = False
                else:
		    motors.setTarget(INTAKE, INTAKE_FWD)	    ## Turn on inner intake.
                    if not motors.getDIO(ARM_LOWER_LIMIT):          ## Turn on arm intake only if arm is lowered.
                        motors.setTarget(ARM_INTAKE, ARM_INTAKE_FWD)## Turn on arm intake.
                    else:
                        motors.setTarget(ARM_INTAKE, MOTOR_OFF)## Turn off arm intake.
            else:
                motors.setTarget(INTAKE, MOTOR_OFF)	## Turn off inner intake.
		motors.setTarget(ARM_INTAKE, MOTOR_OFF) ## Turn off arm intake.


            ## turn thrower on
            ## Called if intake has ball
            ## Control: A
            if j.whenA() and (not throwInProgress):
                throwerConfig = not throwerConfig ## Toggle Thrower.
   
	    ## Push ball back until thrower limit switch off.
            ## Then turn thrower on.
	    ## Turned on and off using the A button.
	    if throwerConfig:
                if not throwerOn:
                    if motors.getDIO(THROWER_LIMIT):
                        motors.setTarget(INTAKE, INTAKE_REV_SLOW)    ## Spin inner intake wheel in reverse.
                    elif (spinCounter < 5) and (not rolledBack) and intakeHasBall:
                        motors.setTarget(INTAKE, INTAKE_REV_SLOW)    ## Spin inner intake wheel in reverse.
                        spinCounter = spinCounter + 1
                    else:
                        motors.setTarget(INTAKE, MOTOR_OFF)     ## Stop inner intake wheel.
                        motors.setTarget(THROWER, throwSpeed)   ## Start thrower motor.
                        throwerOn = True
                        if spinCounter >= 5:
                            rolledBack = True
                        spinCounter = 0
                        throwerConfig = False		## Exit out of this statement.
                else:
                    motors.setTarget(THROWER, MOTOR_OFF)## Turn thrower off.
                    throwerOn = False
                    spinCounter = 0
                    throwerConfig = False		## Exit out of this statement.
				
            ## Speed Of Thrower Motor
            ## Control: Right Joystick
            ## Up: Increment
            ## Down: Decrement
            ## Left: Min power
            ## Right: Max Power
            if throwerOn and (not throwSpeedLock):
                if j.whenRightJoystickUp() and (throwSpeed + THROWER_INC <= THROWER_MAX):
                    throwSpeed = throwSpeed + THROWER_INC
                    motors.setTarget(THROWER, throwSpeed)   ## Start thrower motor.
                    #print "Increment"
                if j.whenRightJoystickDown() and (throwSpeed - THROWER_INC >= THROWER_MIN):
                    throwSpeed = throwSpeed - THROWER_INC
                    motors.setTarget(THROWER, throwSpeed)   ## Start thrower motor.
                    #print "Decrement"
            
            ## Set thrower to max or min speed.
            if j.whenRightJoystickRight() and throwerOn and (not throwSpeedLock):
                throwSpeed = THROWER_MAX
                motors.setTarget(THROWER, throwSpeed)   ## Start thrower motor.
                #print "MAX Speed"
            if j.whenRightJoystickLeft() and throwerOn and (not throwSpeedLock):
                throwSpeed = THROWER_MIN
                motors.setTarget(THROWER, throwSpeed)   ## Start thrower motor.
                #print "MIN Speed"

            ## Lock/Unlock thrower speed
            ## Control: Right Thumbstick
            if j.whenRightThumbstick():
                throwSpeedLock = not throwSpeedLock ## Toggle Thrower speed lock.
                
            ## throw the ball
            ## Called if the thrower is running
	    ## Launch at rising edge. Turn thrower off at falling edge.
            ## Control: Right Trigger
            if j.rightTrigger() > 0.3 and throwerOn: ## Throw ball on rising edge 
                throwInProgress = True
		
            if throwInProgress:
                throwCounter = throwCounter + 1
                motors.setTarget(INTAKE, INTAKE_FWD)
                if (throwCounter >= 25):
                    throwInProgress = False
                    motors.setTarget(INTAKE, MOTOR_OFF)
		    motors.setTarget(ARM_INTAKE, MOTOR_OFF)
                    motors.setTarget(THROWER, MOTOR_OFF)
                    rolledBack = False
                    intakeHasBall = False
                    throwerOn = False
                    throwCounter = 0

            ## Eject Ball
            ## Can be called at any stage of thrower application
            ## Control: B
            if j.B():
		motors.setTarget(THROWER, MOTOR_OFF) 		## Turn thrower off
                throwerOn = False
                ## eject ball ##
                rolledBack = False
                intakeHasBall = False
		motors.setTarget(INTAKE, INTAKE_REV) 		## Spin inner intake wheel in reverse
                if not motors.getDIO(ARM_LOWER_LIMIT):          ## Turn on arm intake only if arm is lowered.
                    motors.setTarget(ARM_INTAKE, ARM_INTAKE_REV)## Turn on arm intake.
                else:
                    motors.setTarget(ARM_INTAKE, MOTOR_OFF)     ## Turn off arm intake.
		pressedB = True
            elif pressedB:
                motors.setTarget(INTAKE, MOTOR_OFF) 		## Turn off inner intake.
                motors.setTarget(ARM_INTAKE, MOTOR_OFF)     	## Turn off arm intake.
		pressedB = False

            ## Nerf Cannons
	    ## Control: Left Trigger - fires continuously.
	    if j.leftTrigger() or j.whenX():
	    	io.output(NERF_CANNONS, False)
	    else:
	    	io.output(NERF_CANNONS, True) #Stop Cannons
                
	### Robot Start Boolean ###
        elif j.Start():
            isStarted = True
            #print "Start"					

	#################################################
        ## Stop motors if controller is not connected. ##
	#################################################
		
        else:
            dt.drive(0, 0) 			    ## Stop driving
            motors.setTarget(INTAKE, MOTOR_OFF)     ## turn off intake
            motors.setTarget(ARM_INTAKE, MOTOR_OFF) ## turn off arm intake
            motors.setTarget(THROWER, MOTOR_OFF)    ## turn off thrower
            io.output(NERF_CANNONS, True)           ## Stop Cannons
            intakeEnabled = False                           
            throwerOn = False
            throwInProgress = False
	    motors.setTarget(ARM, MOTOR_OFF) 	    ## turn off arm
            isStarted = False 			    ## Return to start condition
            #print "Not Connected." 		    ## Print command used for debug

        ## Time interval before next loop begins.
        time.sleep(0.033)

#############################################
## Turn-off configurations on program exit ##
#############################################
except:
    dt.drive(0,0)
    motors.setTarget(INTAKE, MOTOR_OFF)     ## turn off inner intake
    motors.setTarget(ARM_INTAKE, MOTOR_OFF) ## turn off arm intake
    motors.setTarget(THROWER, MOTOR_OFF)    ## turn off thrower
    motors.setTarget(ARM, MOTOR_OFF) 	    ## turn off arm
    io.output(NERF_CANNONS, True)           ## Stop Cannons
    io.cleanup()
    raise
