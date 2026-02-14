import serial
import time
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
CLIENT_URL = os.getenv("REACT_SERVER_URL")  # Your React server URL in .env

# Setup Arduino serial
def init_serial(port="/dev/ttyACM0", baudrate=2000000):
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(3)  # allow Arduino to boot
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return None

# Read data from Arduino
def read_from_arduino(ser):
    if ser is None:
        return None
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            return line
        else:
            return None
    except Exception as e:
        print(f"Error reading from serial: {e}")
        return None

# Prepare info (like your getterSerialPort)
def getterSerialPort():
    return {"Info from": "arduino"}

# Send data to React server
def POSTPayLoadHandler(dataGrabbedArduino):
    if CLIENT_URL is None:
        print("Error: REACT_SERVER_URL not set in .env")
        return

    payload = {
        "arduinoData": dataGrabbedArduino,
        "meta": getterSerialPort()
    }

    try:
        response = requests.post(CLIENT_URL, json=payload)
        print(f"POST Response: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending POST request: {e}")


if __name__ == "__main__":
    ser = init_serial()
    while True:
        data = read_from_arduino(ser)
        if data:
            print(f"Read from Arduino: {data}")
            POSTPayLoadHandler(data)
        time.sleep(0.1)  # prevent busy waiting
