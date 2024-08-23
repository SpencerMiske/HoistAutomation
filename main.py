from time import sleep
import sys
import threading
from Job import job
import serial
import RPi.GPIO as io
from flask import Flask, request, jsonify

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
io.setmode(io.BOARD)

##Initilaize Variables
TANKNUM = 6
STARTRACK = 0
ENDRACK = TANKNUM-1
BACKUP_DISTANCE = 490
HOIST_UP = 0
HOIST_DOWN = 1
speed = 300

relayPower = 12
hoistDir = 16
io.setup(relayPower, io.OUT)
io.setup(hoistDir, io.OUT)
io.output(relayPower,HOIST_DOWN)


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
        speed = job_data[3]
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
    
def hoist_action(tankLoc, direction):
    io.output(hoistDir, HOIST_DOWN)
    io.output(relayPower, HOIST_UP)
    sleep(8)
    io.output(relayPower, HOIST_DOWN)
    move_to(ser, (tankLoc - BACKUP_DISTANCE + BACKUP_DISTANCE*direction), 300)
    io.output(hoistDir, HOIST_UP)
    io.output(relayPower, HOIST_UP)
    sleep(8)
    io.output(relayPower, HOIST_DOWN)
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
                hoist_action(TANKLOC[ENDRACK], 1)
            
                occupiedTanks[ENDRACK] = '0'
            
                move_to(ser, TANKLOC[STARTRACK], speed)
            
                ##Drop rack into tank##
                hoist_action(TANKLOC[STARTRACK], 0)
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

                hoist_action(TANKLOC[nextUp.tankNums[nextUp.currentTank]], 1)
                
                occupiedTanks[nextUp.tankNums[nextUp.currentTank]] = '0'
                
                move_to(ser, TANKLOC[nextUp.next_tank()], speed)
                nextUp.currentTank += 1
                
                hoist_action(TANKLOC[nextUp.tankNums[nextUp.currentTank]], 0)
                
                occupiedTanks[nextUp.tankNums[nextUp.currentTank]] = 'X'
                print(occupiedTanks)
                
                nextUp.start_timer(nextUp.tankTimes[nextUp.currentTank])
                
        sleep(0.1)
############################################################################# 
        
except KeyboardInterrupt:
    print('inturrupted by user')
finally:
    ser.close()
    io.cleanup()



