# purpose: handle the CRUD actions
# to do: GET & POST
from serialScriptMonitor import POSTPayLoadHandler, getterSerialPort # handles how the payload is made
from database import store_reading

# return type: dictionary
def arduinoJSONHandler():
    # will be the handler of deciding get or post request

    # steps of repeated cycle of arduino information
    # 1) get info from arduino & format JSON
    informationCurrent = getHandler() # data type: dictionary


    # 2) send json data to DATABASE
    #dbSendHandler(informationCurrent) # handle the post request to be sent to user

    # final handler of parsed data
    print(informationCurrent) # purpose: JSON formatted from parse (will need to print terminal first)

    # return type: dictionary
    return informationCurrent # will be: what was scanned from arduino

#handler's purpose: increase modularity and make method calls to keep track of sub processes

# purpose: get current Arduino information in JSON format using pyserial lib.
# return type: dictionary
def getHandler():
    return getterSerialPort() # will dive into serialScriptMonitor.py to, return type: dictionary





# purpose: make the payload to client ab arduino info
# argument one is what was returned from getHandler() above
def dbSendHandler(dataGrabbedFromArduino): # handles the full picture of post request sent to client
    if dataGrabbedFromArduino is None:
        return {"DB Status": "No data to send"}

    result = store_reading(dataGrabbedFromArduino["Temperature"], dataGrabbedFromArduino["Humidity"])
    print("Sent to Supabase:", result)
    return result
