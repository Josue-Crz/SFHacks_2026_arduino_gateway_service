"""
Arduino CRUD Handler
Purpose: Handle GET & POST actions between Arduino hardware and frontend client
"""

import os
import requests
import json
from dotenv import load_dotenv
from serialScriptMonitor import POSTPayLoadHandler, getterSerialPort
from database import store_reading

# Load environment variables
load_dotenv()

# Configuration
NGROK_URL = os.getenv('NGROK_URL_TO_CLIENT', 'http://localhost:8000')
CLIENT_ENDPOINT = f"{NGROK_URL}/api/arduino-data"
REQUEST_TIMEOUT = 5  # seconds

def arduinoJSONHandler():
    """
    Main handler for Arduino data cycle
    Returns: Dictionary with Arduino data and status
    """
    # Step 1: Get info from Arduino
    informationCurrent = getHandler()

    # Step 2: Store reading in Supabase
    db_result = None
    if informationCurrent and 'temperatureF' in informationCurrent and 'humidity' in informationCurrent:
        try:
            db_result = store_reading(informationCurrent['temperatureF'], informationCurrent['humidity'])
            print(f"Stored reading in Supabase: {db_result}")
        except Exception as e:
            print(f"Error storing reading in Supabase: {e}")

    # Step 3: Send JSON data to client server
    postResult = postHandler(informationCurrent)

    # Combine results
    return {
        'arduino_data': informationCurrent,
        'db_result': db_result,
        'post_status': postResult
    }

def getHandler():
    """
    Get current Arduino information in JSON format using pyserial
    Returns: Dictionary with sensor data or None if failed
    """
    try:
        # Get data from Arduino via serial port
        arduino_data = getterSerialPort()
        
        if arduino_data is None:
            print("Warning: No data received from Arduino")
            return None
            
        # Validate data structure
        if not isinstance(arduino_data, dict):
            print(f"Error: Arduino data is not a dictionary: {type(arduino_data)}")
            return None
            
        # Optional: Validate required fields
        required_fields = ['humidity', 'temperatureC', 'temperatureF']
        missing_fields = [field for field in required_fields if field not in arduino_data]
        
        if missing_fields:
            print(f"Warning: Missing fields in Arduino data: {missing_fields}")
        
        return arduino_data
        
    except Exception as e:
        print(f"Error in getHandler: {e}")
        return None

def postHandler(dataGrabbedArduino):
    """
    Send Arduino data to frontend client via POST request
    
    Args:
        dataGrabbedArduino: Dictionary containing Arduino sensor data
        
    Returns:
        Dictionary with post status and details
    """
    # Check if Arduino data is valid
    if dataGrabbedArduino is None or not dataGrabbedArduino:
        error_response = {
            "status": "error",
            "message": "Arduino info lacking",
            "data_sent": False
        }
        print(f"Post Error: {error_response['message']}")
        return error_response
    
    # Get client URL from environment
    client_url = os.getenv('NGROK_URL_TO_CLIENT')
    
    if not client_url:
        error_response = {
            "status": "error",
            "message": "NGROK_URL_TO_CLIENT not configured in .env file",
            "data_sent": False
        }
        print(f"Configuration Error: {error_response['message']}")
        return error_response
    
    # Prepare full endpoint URL
    full_endpoint = f"{client_url}/api/arduino-data"
    
    # Attempt to send payload
    try:
        # Create payload using your existing handler
        payload_info = POSTPayLoadHandler(full_endpoint, dataGrabbedArduino)
        
        if payload_info is None:
            raise ValueError("POSTPayLoadHandler returned None")
        
        success_response = {
            "status": "success",
            "message": "Data sent to client successfully",
            "data_sent": True,
            "endpoint": full_endpoint,
            "payload": payload_info
        }
        print(f"✓ Data posted successfully to {full_endpoint}")
        return success_response
        
    except requests.exceptions.Timeout:
        error_response = {
            "status": "error",
            "message": f"Request timeout after {REQUEST_TIMEOUT}s",
            "data_sent": False,
            "endpoint": full_endpoint
        }
        print(f"Timeout Error: Couldn't reach client at {full_endpoint}")
        return error_response
        
    except requests.exceptions.ConnectionError:
        error_response = {
            "status": "error",
            "message": "Connection failed - is the frontend server running?",
            "data_sent": False,
            "endpoint": full_endpoint
        }
        print(f"Connection Error: Frontend not reachable at {full_endpoint}")
        return error_response
        
    except requests.exceptions.RequestException as e:
        error_response = {
            "status": "error",
            "message": f"HTTP request failed: {str(e)}",
            "data_sent": False,
            "endpoint": full_endpoint
        }
        print(f"Request Error: {e}")
        return error_response
        
    except Exception as e:
        error_response = {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "data_sent": False,
            "endpoint": full_endpoint,
            "arduino_data": dataGrabbedArduino
        }
        print(f"Unexpected Error in postHandler: {e}")
        print(f"Arduino data was: {json.dumps(dataGrabbedArduino, indent=2)}")
        return error_response

# Alternative: Direct POST implementation (if you want to bypass POSTPayLoadHandler)
def postHandlerDirect(dataGrabbedArduino):
    """
    Direct POST implementation without using POSTPayLoadHandler
    Use this if you want more control over the request
    """
    if dataGrabbedArduino is None or not dataGrabbedArduino:
        return {
            "status": "error",
            "message": "Arduino info lacking",
            "data_sent": False
        }
    
    client_url = os.getenv('NGROK_URL_TO_CLIENT')
    if not client_url:
        return {
            "status": "error",
            "message": "NGROK_URL_TO_CLIENT not configured",
            "data_sent": False
        }
    
    endpoint = f"{client_url}/api/arduino-data"
    
    try:
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Send POST request
        response = requests.post(
            endpoint,
            json=dataGrabbedArduino,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        
        # Check response
        response.raise_for_status()
        
        return {
            "status": "success",
            "message": "Data sent successfully",
            "data_sent": True,
            "endpoint": endpoint,
            "response_code": response.status_code,
            "response_data": response.json() if response.text else None
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"POST failed: {str(e)}",
            "data_sent": False,
            "endpoint": endpoint
        }

# Testing/Debug function
def testConnection():
    """
    Test the connection to frontend without Arduino data
    """
    test_data = {
        "humidity": 45.5,
        "temperatureC": 22.3,
        "temperatureF": 72.1,
        "soilMoisture": 60,
        "timestamp": "2026-02-14T10:30:00",
        "test_mode": True
    }
    
    print("Testing connection with sample data...")
    result = postHandler(test_data)
    print(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    # Test the connection
    print("=== Arduino Handler Test ===\n")
    testConnection()
