from dotenv import load_dotenv
load_dotenv()

import threading
import time
from flask import Flask, jsonify
from CRUDActions import arduinoJSONHandler
from serialScriptMonitor import getterSerialPort
from database import store_reading, get_latest_reading

app = Flask(__name__)

# In-memory cache of the most recent reading, updated by background thread
latest_reading = None

def serial_reader_loop():
    """Background thread: continuously reads Arduino serial and stores to Supabase."""
    global latest_reading
    while True:
        try:
            data = getterSerialPort()
            if data and 'temperatureF' in data and 'humidity' in data:
                db_result = store_reading(data['temperatureF'], data['humidity'])
                latest_reading = data
                print(f"Background: stored reading {db_result}")
            elif data is None:
                print("Background: no serial data this cycle")
        except Exception as e:
            print(f"Background serial error: {e}")
        time.sleep(5)


@app.route('/api', methods=['GET', 'POST'])
def dataHandler():
    """Legacy endpoint — triggers a serial read + store on demand."""
    dataGrabbedArduino = arduinoJSONHandler()
    dataGrabbedArduino["CALL"] = "SUCCESS TO dataHandler -> arduino information"
    return dataGrabbedArduino


@app.route('/')
def index():
    """Returns the latest cached reading, falling back to DB if cache is empty."""
    if latest_reading:
        return jsonify(latest_reading)

    # Fallback: fetch from database
    db_reading = get_latest_reading()
    if db_reading:
        return jsonify(db_reading)

    return jsonify({"error": "No readings available yet"}), 503


if __name__ == "__main__":
    # Start background serial reader thread (daemon=True so it dies with the app)
    reader_thread = threading.Thread(target=serial_reader_loop, daemon=True)
    reader_thread.start()
    print("Background serial reader thread started")

    app.run(debug=True, use_reloader=False)
