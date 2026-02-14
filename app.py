from dotenv import load_dotenv
load_dotenv()

import threading
import time
from flask import Flask, jsonify
from CRUDActions import arduinoJSONHandler
from serialScriptMonitor import getterSerialPort
from database import store_reading, get_latest_reading

app = Flask(__name__)


def serial_reader_loop():
    """Background thread: read Arduino serial → store in Supabase every 5 seconds."""
    while True:
        try:
            data = getterSerialPort()
            if data and 'temperatureF' in data and 'humidity' in data:
                row = store_reading(data['temperatureF'], data['humidity'])
                print(f"Background: stored reading — {row}")
            else:
                print("Background: no valid data from Arduino")
        except Exception as e:
            print(f"Background: error — {e}")
        time.sleep(5)


@app.route('/api', methods=['GET', 'POST'])
def dataHandler():
    dataGrabbedArduino = arduinoJSONHandler()
    dataGrabbedArduino["CALL"] = "SUCCESS TO dataHandler -> arduino information"
    return dataGrabbedArduino


@app.route('/')
def index():
    latest = get_latest_reading()
    if latest:
        return jsonify(latest)
    return jsonify(dataHandler())


if __name__ == "__main__":
    t = threading.Thread(target=serial_reader_loop, daemon=True)
    t.start()
    app.run(debug=True)
