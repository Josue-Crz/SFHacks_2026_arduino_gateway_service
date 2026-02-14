import serial
import time
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
CLIENT_URL = os.getenv("REACT_SERVER_URL")  # Your React server URL in .env

# Module-level lazy serial connection
_serial_conn = None
_serial_initialized = False

def _get_serial():
    """Lazy-init the serial connection once."""
    global _serial_conn, _serial_initialized
    if not _serial_initialized:
        _serial_initialized = True
        port = os.getenv("SERIAL_PORT", "/dev/ttyACM0")
        baud = int(os.getenv("SERIAL_BAUD", "9600"))
        _serial_conn = init_serial(port, baud)
    return _serial_conn

# Setup Arduino serial
def init_serial(port="/dev/ttyACM0", baudrate=9600):
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(3)  # allow Arduino to boot
        print(f"Serial port {port} opened at {baudrate} baud")
        return ser
    except serial.SerialException as e:
        print(f"Warning: could not open serial port {port}: {e}")
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

def getterSerialPort():
    """Read one line from Arduino, parse 'temperature,humidity' format.
    Returns dict with humidity, temperatureC, temperatureF or None."""
    ser = _get_serial()
    if ser is None:
        return None
    try:
        line = read_from_arduino(ser)
        if not line:
            return None
        parts = line.split(",")
        if len(parts) < 2:
            print(f"Warning: unexpected serial format: {line!r}")
            return None
        temp_f = float(parts[0].strip())
        humidity = float(parts[1].strip())
        temp_c = (temp_f - 32) * 5.0 / 9.0
        return {
            "humidity": humidity,
            "temperatureC": round(temp_c, 2),
            "temperatureF": temp_f,
        }
    except (ValueError, IndexError) as e:
        print(f"Warning: could not parse serial data: {e}")
        return None
    except Exception as e:
        print(f"Error in getterSerialPort: {e}")
        return None

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
