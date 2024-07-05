import RPi.GPIO as io
from time import sleep
import sys
import threading
from Hoist import system
from Job import job

from flask import Flask, request, jsonify

##Initilaize Variables
BUTTONPIN = 11
TANKNUM = 5
IN1 = 16
IN2 = 18
SENSORPIN = 35
STARTRACK = 0
ENDRACK = TANKNUM-1
RACKSPEED = 40

moveQueue = []
endQueue = []
######################

##GPIO Pin Setup
io.setmode(io.BOARD)
zirc = system(TANKNUM, 1, RACKSPEED, 1)
zirc.setMotor(IN1, IN2)
zirc.setSensor(SENSORPIN)
io.setup(BUTTONPIN, io.IN,pull_up_down=io.PUD_UP)
################

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
        new_job = job(job_data[0],job_data[1],job_data[2], moveQueue, endQueue, zirc)
        moveQueue.append(new_job)
        return jsonify({'status': 'success', 'jobID':new_job.jobID}), 200
    except:
        print('could not convert input')
    
def run_server():
    app.run(host='0.0.0.0', port=5000)
    
server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

##Main loop
try:
    while True:
        print(zirc.occupiedTanks)
        
        ##Check if you can move finished rack to the start
        if len(endQueue) != 0 and zirc.occupiedTanks[0] != 'X':
            rackUnloaded = 0
            zirc.moveTo(ENDRACK)
            endQueue.pop(0)
            ##Action to pick up rack##
            sleep(3)
            zirc.occupiedTanks[ENDRACK] = '0'
            
            zirc.moveTo(0)
            
            ##Drop rack into tank##
            sleep(3)
            zirc.occupiedTanks[STARTRACK] = 'X'
            
        
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
                zirc.occupiedTanks[nextUp.tankNums[nextUp.currentTank]] = '0'
                sleep(3)
                
                zirc.moveTo(nextUp.next_tank())
                nextUp.currentTank += 1
                
                ##Drop rack into tank##
                sleep(3)
                zirc.occupiedTanks[nextUp.tankNums[nextUp.currentTank]] = 'X'
                
                nextUp.start_timer(nextUp.tankTimes[nextUp.currentTank])
                
        sleep(0.5)
#############################################################################
        
        
except KeyboardInterrupt:
    print('inturrupted by user')
finally:
    io.cleanup()



