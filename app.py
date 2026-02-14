from flask import Flask, render_template, url_for, request, jsonify
from CRUDActions import arduinoJSONHandler, getHandler, postHandler
app = Flask(__name__)

# FIXME figure out if we need a default JSON, CRUDActions.py file may handle
# data_received = { # purpose: default JSON
#     "message": "Awaiting data"
#     }

global dataGrabbedArduino

@app.route('/api', methods=['GET', 'POST'])
def dataHandler():
    # request json from current data within ngrok
    # return type of arduinoJSONHandler(): dictionary
    dataGrabbedArduino = arduinoJSONHandler() # offload dictionary of POST to user here



    #FIXME
    #handle: what was specifically was  returned from getCRUD()



    # IGNORE WAS A TEST -> handling of additional dictionary information
    dataGrabbedArduino["SUCCESS"] = "CRUD"

    # will inform current end pt ab. what was sent to be displayed in flask server
    return dataGrabbedArduino # return type will be dictionary in order to be JSONIFIED

@app.route('/')
def index():
    return jsonify(dataHandler()) # jsonify argument must be dictionary in order to be jsonified


if __name__ == "__main__":
    app.run(debug=True)

