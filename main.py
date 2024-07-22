import RPi.GPIO as io
from time import sleep
import sys
import threading
from Job import job
import serial

from flask import Flask, request, jsonify

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
##Initilaize Variables
BUTTONPIN = 11
TANKNUM = 5
IN1 = 16
IN2 = 18
SENSORPIN = 40
STARTRACK = 0
ENDRACK = TANKNUM-1
RACKSPEED = 35

ZONENUM = 6
TANKLOC = [0,1000,2000,3000,4000,5000]
occupiedTanks = [0,0,0,0,0,0]

moveQueue = []
endQueue = []
######################

##GPIO Pin Setup
io.setmode(io.BOARD)
io.setup(BUTTONPIN, io.IN,pull_up_down=io.PUD_UP)
################

def send_command(ser, number):
    # Assuming param is an integer that needs to be sent as a 2-byte little-endian value
    number_bytes = number.to_bytes(2, byteorder='little')
    
    ser.write(number_bytes)
    
def move_to(tankNum):
    send_command(ser, TANKLOC[tankNum])
    response = ser.readline().decode().strip()
    while(response != "DONE"):
        sleep(0.1)
        response = ser.readline().decode().strip()

#End rack unloaded button
def button_callback(channel):
    print('Rack has been unloaded')
    rackUnloaded = 1
    
io.add_event_detect(BUTTONPIN, io.FALLING, callback=button_callback, bouncetime=200)

#Flask server to accept jobs
app = Flask(__name__)
@app.route('/add_job_list',methods=['POST'])
def add_job_list():
    try:
        job_data = request.json #expecting a list format
        new_job = job(job_data[0],job_data[1],job_data[2], moveQueue, endQueue, occupiedTanks)
        moveQueue.append(new_job)
        return jsonify({'status': 'success', 'jobID':new_job.jobID}), 200
    except:
        print('could not convert input')
    
def run_server():
    app.run(host='0.0.0.0', port=5000)
    
    
    ser.write(number_bytes)
    
server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

##Main loop
try:
    while True:
        ##Check if you can move finished rack to the start
        if len(endQueue) != 0 and occupiedTanks[0] != 'X':
            rackUnloaded = 0
            move_to(ENDRACK)
            endQueue.pop(0)
            ##Action to pick up rack##
            sleep(3)
            occupiedTanks[ENDRACK] = '0'
            
            moveTo(STARTRACK)
            
            ##Drop rack into tank##
            sleep(3)
            occupiedTanks[STARTRACK] = 'X'
            
        
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
            
                move_to(nextUp.tankNums[nextUp.currentTank])
                
                ##Action to pick up rack##
                occupiedTanks[nextUp.tankNums[nextUp.currentTank]] = '0'
                sleep(3)
                
                move_to(nextUp.next_tank())
                nextUp.currentTank += 1
                
                ##Drop rack into tank##
                sleep(3)
                occupiedTanks[nextUp.tankNums[nextUp.currentTank]] = 'X'
                
                nextUp.start_timer(nextUp.tankTimes[nextUp.currentTank])
                
        sleep(0.5)
#############################################################################
        
        
except KeyboardInterrupt:
    print('inturrupted by user')
finally:
    io.cleanup()
    ser.close()



