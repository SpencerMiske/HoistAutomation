from time import sleep
import sys
import threading
from Job import job
import serial

from flask import Flask, request, jsonify

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

##Initilaize Variables
TANKNUM = 6
STARTRACK = 0
ENDRACK = TANKNUM-1
BACKUP_DISTANCE = 490

TANKLOC = [500,1600,2700,3800,4900,6000]
occupiedTanks = [0,0,0,0,0,0]

latest_message = None
unloaded = 0
message_lock = threading.Lock()
unloaded_lock = threading.Lock()

moveQueue = []
endQueue = []
#######################################################################################
#Defining functions (wanted this in a separate file but the threading was being weird)
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

def move_to(ser, tankLoc, speed):
    global latest_message
    
    send_command(ser, tankLoc, speed)
    
    while True:
        with message_lock:
            if latest_message == 'Move Done':
                latest_message = None
                break
        sleep(0.1)
        
def send_command(ser, number, speed):
    # Assuming param is an integer that needs to be sent as a 2-byte little-endian value
    number_bytes = number.to_bytes(2, byteorder='little')
    ser.write(number_bytes)
    
    speed_bytes = speed.to_bytes(2, byteorder='little')
    ser.write(speed_bytes)
        
def pick_up(tankLoc):
    #Lower hoist
    sleep(3)
    move_to(ser, tankLoc, 300)
    #Rasie Hoist
    sleep(3)

def lower(tankLoc):
    #Lower Hoist
    sleep(3)
    move_to(ser, tankLoc - BACKUP_DISTANCE, 300)
    #Raise
    sleep(3)
#######################################################################################

##Main loop
try:
    while True:
        ##Check if you can move finished rack to the start
        with unloaded_lock:
            if len(endQueue) != 0 and occupiedTanks[0] != 'X' and unloaded == 1:
                unloaded = 0
                move_to(ser, TANKLOC[ENDRACK] - BACKUP_DISTANCE, 600)
                endQueue.pop(0)
                ##Action to pick up rack##
                pick_up(TANKLOC[ENDRACK])
            
                occupiedTanks[ENDRACK] = '0'
            
                move_to(ser, TANKLOC[STARTRACK], 200)
            
                ##Drop rack into tank##
                lower(TANKLOC[STARTRACK])
                print(occupiedTanks)
            
        
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
                print('moving job ' + str(nextUp.jobID) + 'to tank: ' + str(TANKLOC[nextUp.tankNums[nextUp.currentTank]]))

                move_to(ser, (TANKLOC[nextUp.tankNums[nextUp.currentTank]]) - BACKUP_DISTANCE, 600)

                ##Action to pick up rack##
                pick_up(TANKLOC[nextUp.tankNums[nextUp.currentTank]])
                
                occupiedTanks[nextUp.tankNums[nextUp.currentTank]] = '0'
                
                move_to(ser, TANKLOC[nextUp.next_tank()],200)
                nextUp.currentTank += 1
                
                ##Drop rack into tank##
                lower(TANKLOC[nextUp.tankNums[nextUp.currentTank]])
                
                occupiedTanks[nextUp.tankNums[nextUp.currentTank]] = 'X'
                print(occupiedTanks)
                
                nextUp.start_timer(nextUp.tankTimes[nextUp.currentTank])
                
        sleep(0.1)
#############################################################################
        
        
except KeyboardInterrupt:
    print('inturrupted by user')
finally:
    ser.close()



