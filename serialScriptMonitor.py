import serial
import os
import time

# Lazy-initialized serial connection — no crash at import time
_serial_obj = None


def _get_serial():
    """Open serial port on first use, using env vars SERIAL_PORT and SERIAL_BAUD."""
    global _serial_obj
    if _serial_obj is not None:
        return _serial_obj

    port = os.getenv('SERIAL_PORT', '/dev/ttyACM0')
    baud = int(os.getenv('SERIAL_BAUD', '9600'))

    _serial_obj = serial.Serial(port, baudrate=baud, bytesize=8, parity='N', stopbits=1)
    time.sleep(3)  # allow the Arduino to boot
    return _serial_obj


def getterSerialPort():
    """
    Read one line from the Arduino serial port.
    Expects format: "temperature,humidity\\n"
    Returns dict with temperatureF, temperatureC, humidity — or None on failure.
    """
    try:
        ser = _get_serial()
        raw = ser.readline().decode('utf-8').strip()
        if not raw:
            return None

        parts = raw.split(',')
        if len(parts) < 2:
            print(f"Warning: unexpected serial format: {raw}")
            return None

        temp_f = float(parts[0])
        humidity = float(parts[1])
        temp_c = (temp_f - 32) * 5.0 / 9.0

        return {
            "temperatureF": round(temp_f, 2),
            "temperatureC": round(temp_c, 2),
            "humidity": round(humidity, 2),
        }
    except (serial.SerialException, OSError) as e:
        print(f"Warning: could not open serial port: {e}")
        return None
    except (ValueError, IndexError) as e:
        print(f"Warning: failed to parse serial data: {e}")
        return None


def POSTPayLoadHandler(clientURL, dataGrabbedArduino):
    """Forward Arduino data to a client URL via POST (kept for CRUDActions compatibility)."""
    import requests
    try:
        resp = requests.post(clientURL, json=dataGrabbedArduino, timeout=5)
        return {"status": resp.status_code, "url": clientURL}
    except Exception as e:
        print(f"POSTPayLoadHandler error: {e}")
        return None
