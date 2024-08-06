import serial

def add_job_list():
    try:
        job_data = request.json #expecting a list format
        new_job = job(job_data[0],job_data[1],job_data[2], moveQueue, endQueue, occupiedTanks)
        moveQueue.append(new_job)
        occupiedTanks[STARTRACK] = 'X'
        return jsonify({'status': 'success', 'jobID':new_job.jobID}), 200
    except:
        print('could not convert input')

def send_command(ser, number):
    # Assuming param is an integer that needs to be sent as a 2-byte little-endian value
    number_bytes = number.to_bytes(2, byteorder='little')
    ser.write(number_bytes)
    
def move_to(tankLoc):
    global response_message
    
    send_command(ser, tankLoc)
    
    while True:
        with response_lock:
            if response_message == 'DONE':
                response_message = None
                break
        sleep(0.1)
        
def pick_up(tankLoc):
    move_to(tankLoc - BACKUP_DISTANCE)
    #Lower hoist
    sleep(2)
    move_to(tankLoc)
    #Rasie Hoist
    sleep(2)
    
def lower(tankLoc):
    #Lower Hoist
    sleep(2)
    move_to(tankLoc - BACKUP_DISTANCE)
    #Raise
    sleep(2)
