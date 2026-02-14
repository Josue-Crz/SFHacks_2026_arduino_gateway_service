from dotenv import load_dotenv
load_dotenv()

import threading
import time
from flask import Flask, jsonify
from CRUDActions import arduinoJSONHandler
from serialScriptMonitor import getterSerialPort
from database import store_reading, get_latest_reading

app = Flask(__name__)

#Priority return data on console as dictionary
def serial_reader_loop():
    """Background thread: read Arduino serial → store in Supabase every 5 seconds."""
    while True:
        try:
            data = getterSerialPort()
        except Exception as e:
            print(f"Background: error — {e}")
            return None
        time.sleep(5) # delay for each buffer read

        return dict(data)

# ignore for now
@app.route('/api', methods=['GET', 'POST'])
def dataHandler():
    dataGrabbedArduino = arduinoJSONHandler() # data type: dictionary
    dataGrabbedArduino["CALL"] = "SUCCESS END OP OF dataHandler -> arduino information"

    return dataGrabbedArduino

# output of the json IGNORE FOR NOW
@app.route('/')
def index():
    return jsonify(dataHandler())


if __name__ == "__main__":
    app.run(debug=True)
