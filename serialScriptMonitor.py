import serial
import time

SerialObj = serial.Serial('/dev/ttyACM0')

# settings of serial ports:
SerialObj.baudrate = 2000000
SerialObj.bytesize = 8
SerialObj.parity = 'N'
SerialObj.stopbits = 1
time.sleep(3) # allow the Arduino to boot

# input from user on client
SerialWriteBuffer = None

# handle what the serial I/O looks like
def POSTPayLoadHandler():
    # handles how the JSON return is formatted
    return dict({"payload format returned" : "test"}) # must return to POST payload as DICTIONARY TO DISPLAY FLASK SERVER PROPERLY