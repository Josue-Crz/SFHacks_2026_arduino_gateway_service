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


# gets actual information of serial port
def getterSerialPort():
    return dict({"Info from ": " arduino"})

# this will handle the POST request to client after getterSerialPort() method in this file that handled serial py
def POSTPayLoadHandler(clientURL, dataGrabbedArduino):
    pass # fixme: grab Luis's REACT server url and safely put into .env file