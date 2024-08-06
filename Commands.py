import serial

def send_command(ser, number):
    # Assuming param is an integer that needs to be sent as a 2-byte little-endian value
    number_bytes = number.to_bytes(2, byteorder='little')
    ser.write(number_bytes)
        
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
    sleep(2)tankTimes


