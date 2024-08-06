from time import sleep
import sys
import threading
from Job import job
import serial
from Commands import send_command,move_to,pick_up,lower

from flask import Flask, request, jsonify

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
##Initilaize Variables
TANKNUM = 6
STARTRACK = 0
ENDRACK = TANKNUM-1
BACKUP_DISTANCE = 100

TANKLOC = [0,1200,2400,3600,4800,6000]
occupiedTanks = [0,0,0,0,0,0]

latest_message = None
unloaded = 0
message_lock = threading.Lock()
unloaded_lock = threading.Lock()

moveQueue = []
endQueue = []
######################
def read_from_clearcore():
    global latest_message
    global unloaded
    
    while True:
        try:
            message = ser.readline().decode().strip()
            if message:
                with message_lock:
                    latest_message = message
                print(f'recieved: {message}')
                
                if message == 'UNLOAD':
                    with unloaded_lock:
                        unloaded = 1
                
        except Exception as e:
            print(f'Error reading from the Clearcore: {e}')

#Flask server to accept jobs
app = Flask(__name__)
@app.route('/add_job_list',methods=['POST'])
def add_job_list():
    try:
        job_data = request.json #expecting a list format
        new_job = job(job_data[0],job_data[1],job_data[2], moveQueue, endQueue, occupiedTanks)
        moveQueue.append(new_job)
        occupiedTanks[STARTRACK] = 'X'
        return jsonify({'status': 'success', 'jobID':new_job.jobID}), 200
    except:
        print('could not convert input')

def run_server():
    app.run(host='0.0.0.0', port=5000)
    
server_thread = threading.Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

serial_thread = threading.Thread(target=read_from_clearcore)
serial_thread.daemon = True
serial_thread.start()

##Main loop
try:
    while True:
        ##Check if you can move finished rack to the start
        with unloaded_lock:
            if len(endQueue) != 0 and occupiedTanks[0] != 'X' and unloaded == 1:
                unloaded = 0
                move_to(ser, TANKLOC[ENDRACK])
                endQueue.pop(0)
                ##Action to pick up rack##
                pick_up(ANKLOC[ENDRACK])
            
                occupiedTanks[ENDRACK] = '0'
            
                move_to(ser, TANKLOC[STARTRACK])
            
                ##Drop rack into tank##
                lower(TANKLOC[STARTRACK])
            
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
            
                move_to(ser, TANKLOC[nextUp.tankNums[nextUp.currentTank]])
                
                ##Action to pick up rack##
                pick_up(TANKLOC[nextUp.tankNums[nextUp.currentTank]])
                
                occupiedTanks[nextUp.tankNums[nextUp.currentTank]] = '0'
                
                move_to(ser, TANKLOC[nextUp.next_tank()])
                nextUp.currentTank += 1
                
                ##Drop rack into tank##
                lower(TANKLOC[nextUp.next_tank()])
                
                occupiedTanks[nextUp.tankNums[nextUp.currentTank]] = 'X'
                
                nextUp.start_timer(nextUp.tankTimes[nextUp.currentTank])
                
        sleep(0.1)
#############################################################################
        
        
except KeyboardInterrupt:
    print('inturrupted by user')
finally:
    io.cleanup()
    ser.close()



