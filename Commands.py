def send_command(ser, number):
    # Assuming param is an integer that needs to be sent as a 2-byte little-endian value
    number_bytes = number.to_bytes(2, byteorder='little')
    
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
