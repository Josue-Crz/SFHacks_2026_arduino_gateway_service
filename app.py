from flask import Flask, render_template, url_for, request, jsonify
from CRUDActions import arduinoJSONHandler, getHandler, postHandler
from database import store_reading, get_latest_reading
app = Flask(__name__)

@app.route('/api', methods=['GET', 'POST'])
def dataHandler():
    # request json from current data within ngrok
    # return type of arduinoJSONHandler(): dictionary
    dataGrabbedArduino = arduinoJSONHandler() # offload dictionary of POST to user here




    # IGNORE WAS A TEST to see if data handler method works
    dataGrabbedArduino["CALL"] = "SUCCESS TO dataHandler -> arduino information"

    # will inform current end pt ab. what was sent to be displayed in flask server
    return dataGrabbedArduino # return type will be dictionary in order to be JSONIFIED

@app.route('/')
def index():
    return jsonify(dataHandler()) # jsonify argument must be dictionary in order to be jsonified


if __name__ == "__main__":
    app.run(debug=True)

