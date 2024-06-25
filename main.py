import RPi.GPIO as io
from time import sleep
import sys
from Hoist import system

##Setup
io.setmode(io.BOARD)

##Initilaize Variables
buttonPin = 11
ledPin = 13
buttonState = 0

tankNum = 5
in1 = 16
in2 = 18

##GPIO Pin Setup
zirc = system(tankNum, 2, 50)
zirc.setMotor(in1, in2)

io.setup(buttonPin, io.IN,pull_up_down=io.PUD_UP)
io.setup(ledPin, io.OUT)
io.output(ledPin, 1)

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
        
        command = int(input('Next tank ready: '))
        if command > zirc.zones: print('tank not in range')
        else: zirc.moveTo(command-1)
        
except KeyboardInterrupt:
    print('inturrupted by user')
finally:
    io.cleanup()
