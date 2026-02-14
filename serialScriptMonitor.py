import serial
import os
import time

# initialize arduino data
SerialObj = serial.Serial('/dev/ttyACM0')

SerialObj.baudrate = 2000000
SerialObj.bytesize = 8
SerialObj.parity = 'N'
SerialObj.stopbits = 1
time.sleep(3) # wait for the Arduino to boot up




def getterSerialPort():
    # parse the data
    #lineBytes = SerialObj.readline()
    tempHumidJSON = dict()

    tempHumidJSON["Temperature"] = str(SerialObj.readline().decode('utf-8').strip())
    tempHumidJSON["Humidity"] = str(SerialObj.readline().decode('utf-8').strip())



    return tempHumidJSON


def POSTPayLoadHandler(clientURL, dataGrabbedArduino):
    """Forward Arduino data to a client URL via POST (kept for CRUDActions compatibility)."""
    import requests
    try:
        resp = requests.post(clientURL, json=dataGrabbedArduino, timeout=5)
        return {"status": resp.status_code, "url": clientURL}
    except Exception as e:
        print(f"POSTPayLoadHandler error: {e}")
        return None
