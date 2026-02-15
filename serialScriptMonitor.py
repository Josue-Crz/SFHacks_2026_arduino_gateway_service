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

    temp_raw = SerialObj.readline().decode('utf-8').strip()   # e.g. "T=20.0"
    humid_raw = SerialObj.readline().decode('utf-8').strip()  # e.g. "Humidity=53.0"

    tempHumidJSON["Temperature"] = float(temp_raw.split('=')[1])
    tempHumidJSON["Humidity"] = float(humid_raw.split('=')[1])


    print(tempHumidJSON)
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
