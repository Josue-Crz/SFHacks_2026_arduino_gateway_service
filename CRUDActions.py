# purpose: handle the CRUD actions
# to do: GET & POST

from serialScriptMonitor import POSTPayLoadHandler, getterSerialPort # handles how the payload is made

# return type: dictionary
def arduinoJSONHandler():
    # will be the handler of deciding get or post request

    # steps of repeated cycle of arduino information
    # 1) get info from arduino
    informationCurrent = getHandler() # handle getting the data from arduino hardware
    # 2) send json data to client server
    postHandler(informationCurrent) # handle the post request to be sent to user

    return informationCurrent # will be: what was scanned from arduino

#handler's purpose: increase modularity and make method calls to keep track of sub processes

# purpose: get current Arduino information in JSON format using pyserial lib.
# return type: dictionary
def getHandler():
    # FIXME: this section will use pyserial to grab info from arduino w/ respective getter method
    return getterSerialPort()

# purpose: make the payload to client ab arduino info
# argument one is what was given from getHandler()
def postHandler(dataGrabbedArduino): # handles the full picture of post request sent to client
    # datagrabbed from arduino is empty
    if (dataGrabbedArduino == None):
        return dict({"Status": "Arduino info lacking"})

    payLoadInfo = None
    NGROKURLTOCLIENT = None #FIXME you need to grab FRONTEND SERVER URL from .env
    clientURL = NGROKURLTOCLIENT # Grab client endpoint to make POST requests to client server about arduino data

    #now make a try-except for payload
    try:
        payLoadInfo = POSTPayLoadHandler(clientURL, dataGrabbedArduino)  # returns dict
    except:
        print("Couldn't make payload to client", payLoadInfo) # prints out the data of payLoadInfo

    return payLoadInfo # returns what was sent to client within middle man handling (return type: dictionary)