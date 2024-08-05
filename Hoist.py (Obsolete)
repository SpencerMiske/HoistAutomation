##Hoist Class
##NOW OBSOLETE WITH CLEARCORE MOTORS

import RPi.GPIO as io
from time import sleep

io.cleanup()

class system:
    
    occupiedTanks = []
    
    def __init__(self, zones, initialZone, hoistSpeed, home):
        self.zones = zones
        self.speed = hoistSpeed
        self.currentZone = initialZone
        self.home = home
        
        for i in range(zones):
            self.occupiedTanks.append('0')
        
        
    def setMotor(self, in1, in2):
        io.setup(in1, io.OUT)
        io.setup(in2, io.OUT)
        
        self.backward = io.PWM(in2, 1000)
        self.backward.start(0)

        self.forward = io.PWM(in1, 1000)
        self.forward.start(0)
    
    def setSensor(self, pin):
        io.setup(pin, io.IN,pull_up_down=io.PUD_UP)
        self.sensorPin = pin
    
    def move(self, speed):
        if speed > 0:
            self.forward.ChangeDutyCycle(self.speed)
            self.backward.ChangeDutyCycle(0)
        elif speed == 0:
            self.forward.ChangeDutyCycle(0)
            self.backward.ChangeDutyCycle(0)
        else:
            self.forward.ChangeDutyCycle(0)
            self.backward.ChangeDutyCycle(self.speed)
            

        
    def moveTo(self, endZone):
        
        if endZone > self.currentZone: direction = 1
        else: direction = -1
        
        print('moving')##Hoist Class

import RPi.GPIO as io
from time import sleep

io.cleanup()

class system:
    
    occupiedTanks = []
    
    def __init__(self, zones, initialZone, hoistSpeed, home):
        self.zones = zones
        self.speed = hoistSpeed
        self.currentZone = initialZone
        self.home = home
        
        for i in range(zones):
            self.occupiedTanks.append('0')
        
        
    def setMotor(self, in1, in2):
        io.setup(in1, io.OUT)
        io.setup(in2, io.OUT)
        
        self.backward = io.PWM(in2, 100)
        self.backward.start(0)

        self.forward = io.PWM(in1, 100)
        self.forward.start(0)
    
    def setSensor(self, pin):
        io.setup(pin, io.IN,pull_up_down=io.PUD_UP)
        self.sensorPin = pin
    
    def move(self, speed):
        if speed > 0:
            self.forward.ChangeDutyCycle(self.speed)
            self.backward.ChangeDutyCycle(0)
        elif speed == 0:
            self.forward.ChangeDutyCycle(0)
            self.backward.ChangeDutyCycle(0)
        else:
            self.forward.ChangeDutyCycle(0)
            self.backward.ChangeDutyCycle(self.speed)
            

        
    def moveTo(self, endZone):
        
        if endZone > self.currentZone: direction = 1
        else: direction = -1
        
        print('moving')
        
        self.move(self.speed*direction)
        
        checkHistory = io.input(self.sensorPin)
       
        while self.currentZone != endZone:
            sleep(0.01)
            check = io.input(self.sensorPin)

        
        self.move(self.speed*direction)
        
        checkHistory = io.input(self.sensorPin)
       
        while self.currentZone != endZone:
            sleep(0.01)
            check = io.input(self.sensorPin)
            
            if check == 1 and checkHistory != check:
                self.currentZone += direction
            checkHistory = check
                
        print('stop moving')
        self.move(0)

        print('Destination Reached')

            

