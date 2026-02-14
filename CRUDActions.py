# purpose: handle the CRUD actions
# to do: GET & POST
from serialScriptMonitor import POSTPayLoadHandler, getterSerialPort # handles how the payload is made

import psycopg2
from psycopg2.extras import Json

# return type: dictionary
def arduinoJSONHandler():
    # will be the handler of deciding get or post request

    # steps of repeated cycle of arduino information
    # 1) get info from arduino & format JSON
    informationCurrent = getHandler() # data type: dictionary


    # 2) send json data to DATABASE
    dbSendHandler(informationCurrent) # handle the post request to be sent to user

    # final handler of parsed data
    print(informationCurrent) # purpose: JSON formatted from parse (will need to print terminal first)

    # return type: dictionary
    return informationCurrent # will be: what was scanned from arduino

#handler's purpose: increase modularity and make method calls to keep track of sub processes

# purpose: get current Arduino information in JSON format using pyserial lib.
# return type: dictionary
def getHandler():
    # FIXME: this section will use pyserial to grab info from arduino w/ respective getter method
    return getterSerialPort() # will dive into serialScriptMonitor.py to, return type: dictionary





# purpose: make the payload to client ab arduino info
# argument one is what was returned from getHandler() above
def dbSendHandler(dataGrabbedFromArduino): # handles the full picture of post request sent to client
    if(dataGrabbedFromArduino == None):
        return dict({"Empty": "Empty JSON"})

    #CONN_STRING -> .env var

    # MAJOR TO DO:
    # sending data of JSON Arduino data in Python -> Postgresql DB
    try:
        # init logic credentials
        conn = psycopg2.connect("dname=test user=postgres password=secret")
        cur = conn.cursor()

        # execution to db
        cur.execute(
            "INSERT INTO profiles (settings) VALUES (%s)",
            (Json(dataGrabbedFromArduino),)
        )

        conn.commit()
        print("JSON SENT TO POSTGRESQL")


    finally: # close all connection
        if conn:
            cur.close()
            conn.close()

    return dict({"DB Status": "Sent to DB Success"})