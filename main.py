import RPi.GPIO as io
from time import sleep
import sys
import threading
from Hoist import system
from Job import job

##Initilaize Variables
buttonPin = 11
buttonState = 0
tankNum = 4
in1 = 16
in2 = 18
sensorPin = 40
STARTRACK = 0
ENDRACK = tankNum-1
rackUnloaded = 0

moveQueue = []
endQueue = []
######################

##GPIO Pin Setup
io.setmode(io.BOARD)
zirc = system(tankNum, 2, 40, 1)
zirc.setMotor(in1, in2)
zirc.setSensor(sensorPin)
io.setup(buttonPin, io.IN,pull_up_down=io.PUD_UP)
################

##Adding jobs to queue for testing
job1 = job(1, ['START',10,10,'END'], [STARTRACK,1,2,ENDRACK], moveQueue, endQueue, zirc)
job2 = job(2, ['START',10,10,'END'], [STARTRACK,1,2,ENDRACK], moveQueue, endQueue, zirc)
moveQueue.append(job1)
moveQueue.append(job2)
#################################

#End rack unloaded button
def button_callback(channel):
    print('Rack has been unloaded')
    rackUnloaded = 1
    
io.add_event_detect(buttonPin, io.FALLING, callback=button_callback, bouncetime=200)
######################

##Main loop
try:
    while True:
        print(zirc.occupiedTanks)
        
        ##Check if you can move finished rack to the start
        if len(endQueue) != 0 and zirc.occupiedTanks[0] != 'X' and rackUnloaded == 1:
            rackUnloaded = 0
            zirc.moveTo(tankNum)
            
            ##Action to pick up rack##
            sleep(3)
            zirc.occupiedTanks[tankNum] = '0'
            
            zirc.moveTo(0)
            
            ##Drop rack into tank##
            sleep(3)
            zirc.occupiedTanks[tankNum] = 'X'
            
        
        ##If there are jobs to move
        if len(moveQueue) != 0:
            i = 0
            nextUp = moveQueue[i]
            ##Find a job that is doable
            while nextUp.cantDo():
                i += 1
                if i >= len(moveQueue):
                    break
                nextUp = moveQueue[i]
                
            if i < len(moveQueue):
                nextUp = moveQueue.pop(i)
                print('moving job ' + str(nextUp.jobID))
            
                zirc.moveTo(nextUp.tankNums[nextUp.currentTank])
                
                ##Action to pick up rack##
                zirc.occupiedTanks[nextUp.currentTank] = '0'
                sleep(3)
                
                zirc.moveTo(nextUp.next_tank())
                nextUp.currentTank += 1
                
                ##Drop rack into tank##
                sleep(3)
                zirc.occupiedTanks[nextUp.currentTank] = 'X'
                
                nextUp.start_timer(nextUp.tankTimes[nextUp.currentTank])
        sleep(0.5)
#############################################################################
        
        
except KeyboardInterrupt:
    print('inturrupted by user')
finally:
    io.cleanup()

