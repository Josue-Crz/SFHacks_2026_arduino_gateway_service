# purpose: handle the CRUD actions
# to do: GET & POST

from serialScriptMonitor import POSTPayLoadHandler # handles how the payload is made

# return type: dictionary
def arduinoJSONHandler():
    # will be the handler of deciding get or post request

    # steps of repeated cycle of arduino information
    # 1) get info from arduino
    informationCurrent = getHandler() # handle getting the data from arduino hardware
    # 2) send json data to client server
    postHandler(informationCurrent) # handle the post request to be sent to user

    return informationCurrent # will be: what was scanned from arduino

# purpose: get current Arduino information in JSON format using pyserial lib.
def getHandler():
    return POSTPayLoadHandler() # get current information from arduino

# purpose: make the payload to client ab arduino info
# argument one is what was given from getHandler()
def postHandler(dataGrabbedArduino): # handles the full picture of post request sent to client
    NGROKURLTOCLIENT = None #FIXME you need to grab FRONTEND SERVER URL from .env
    clientURL = NGROKURLTOCLIENT # Grab client endpoint to make POST requests to client server about arduino data


    #FIXME: make secondary measure that POST request wasn't empty
    # possible try-except block here for makePayload safety

    #FIXME configure the payload from serialScriptMonitor.py's to make a POST request to client
    # next line makes the POST request
    # makePayload(clientURL, postJSONPayload) # make payload from getter to here

    return "Test" # returns what was sent to client