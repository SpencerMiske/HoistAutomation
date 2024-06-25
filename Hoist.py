##Hoist Class

import RPi.GPIO as io

class system:
    
    def __init__(self, zones, initialZone, in1, in2, hoistSpeed):
        self.zones = zones
        self.speed = hoistSpeed
        self.currentZone = initialZone
        
        io.setup(in1, io.OUT)
        io.setup(in2, io.OUT)
        
        backward = io.PWM(in2, 100)
        backward.start(0)

        forward = io.PWM(in1, 100)
        forward.start(0)
    
    def move(self, speed):
        if speed > 0:
            forward.ChangeDutyCycle(speed)
            backward.ChangeDutyCycle(0)
        else:
            forward.ChangeDutyCycle(0)
            backward.ChangeDutyCycle(speed)
            
    def stop():
        forward.ChangeDutyCycle(0)
        backward.ChangeDutyCycle(0)
        
    def moveTo(self, endZone):
        if endZone > currentZone: direction = 1
        else direction = -1
        
        self.move(speed*direction)
        
        while currentZone != endZone:
            buttonState = io.input(buttonPin)
            
            if buttonState = 0:
                currentZone += direction
                
        self.stop
        print('Destination Reached')

            