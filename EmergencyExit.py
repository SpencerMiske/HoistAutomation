import RPi.GPIO as io
from time import sleep
import sys

##Setup
io.setmode(io.BOARD)
################################

##Initilaize Variables
buttonPin = 11
ledPin = 13
buttonState = 0
################################

##GPIO Pin Setup
io.setup(buttonPin, io.IN,pull_up_down=io.PUD_UP)
io.setup(ledPin, io.OUT)
################################

#Emergency exit button
def button_callback(channel):
    print('Exit button pressed')
    io.cleanup()
    sys.exit(0)    
io.add_event_detect(buttonPin, io.FALLING, callback=button_callback, bouncetime=200)

try:
    print('Start')
    while True:
        ##Main looping code
        
except KeyboardInterrupt:
    print('inturrupted by user')
finally:
    io.cleanup()