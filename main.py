import RPi.GPIO as io
from time import sleep
import sys
import threading
from Hoist import system
from Job import job


##Setup
io.setmode(io.BOARD)

##Initilaize Variables
buttonPin = 11
ledPin = 13
buttonState = 0

tankNum = 7
in1 = 16
in2 = 18
sensorPin = 40

moveQueue = []
endQueue = []

##GPIO Pin Setup
zirc = system(tankNum, 2, 30, 3)
zirc.setMotor(in1, in2)
zirc.setSensor(sensorPin)

job1 = job(1, [10,10,10,10,10], [1,2,3,4,5], moveQueue, endQueue, zirc)
job2 = job(2, [10,10,10,10,10], [1,2,3,4,5], moveQueue, endQueue, zirc)
job3 = job(3, [10,10,10,10,10], [1,2,3,4,5], moveQueue, endQueue, zirc)
moveQueue.append(job1)
moveQueue.append(job2)
moveQueue.append(job3)

io.setup(buttonPin, io.IN,pull_up_down=io.PUD_UP)
io.setup(ledPin, io.OUT)
io.output(ledPin, 1)

#Wait for button press to start
while True:
    buttonCheck = io.input(buttonPin)
    if buttonCheck == 0:
        sleep(0.5)
        break
    sleep(0.1)

#Emergency exit button
def button_callback(channel):
    
    print('Exit button pressed')
    io.output(ledPin,0)
    io.cleanup()
    sys.exit(0)
    
io.add_event_detect(buttonPin, io.FALLING, callback=button_callback, bouncetime=200)

try:
    print('Start')
    while True:
        if len(moveQueue) > 0:
            i = 0
            nextUp = moveQueue[i]
            while zirc.occupiedTanks[nextUp.next_tank()] == 'x':
                i +=1
                nextUp = moveQueue[i]
            
            zirc.moveTo(nextUp.tankNums[nextUp.currentTank])
            ##Action to pick up rack
            sleep(5)
            zirc.moveTo(nextUp.next_tank())
            nextUp.currentTank += 1
            ##Drop rack into tank
            nextUp.start_timer(nextUp.tankTimes[nextUp.currentTank])
            
            
        elif zirc.currentZone != zirc.home:
            if zirc.currentZone > zirc.home: zirc.move(-1*(zirc.speed))
            else: zirc.move(zirc.speed)
            sleep(0.05)
        else:
            sleep(0.5)
            
        
except KeyboardInterrupt:
    print('inturrupted by user')
finally:
    io.cleanup()

