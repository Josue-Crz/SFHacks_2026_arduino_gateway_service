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
    baud = int(os.getenv('SERIAL_BAUD', '2000000'))

    _serial_obj = serial.Serial(port, baudrate=baud, bytesize=8, parity='N', stopbits=1)
    time.sleep(3)  # allow the Arduino to boot
    return _serial_obj


def getterSerialPort():
    """
    Read two lines from the Arduino serial port.
    Expects format:
        T=<value>        (Celsius, from DHT11)
        Humidity=<value>
    Returns dict with temperatureF, temperatureC, humidity — or None on failure.
    """
    try:
        ser = _get_serial()
        readings = {}

        for _ in range(2):
            raw = ser.readline().decode('utf-8').strip()
            if not raw or '=' not in raw:
                print(f"Warning: unexpected serial format: {raw}")
                return None
            key, value = raw.split('=', 1)
            readings[key.strip()] = float(value.strip())

        if 'T' not in readings or 'Humidity' not in readings:
            print(f"Warning: missing expected keys, got: {list(readings.keys())}")
            return None

        temp_c = readings['T']
        humidity = readings['Humidity']
        temp_f = temp_c * 9.0 / 5.0 + 32

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
