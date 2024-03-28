import requests
import schedule
import time
import json
from request import Request

NOGGIN_URL = "http://127.0.0.1:5000"  # Adjust the URL/port as necessary
AUTH_TOKEN = "YourAuthorizationKeyHere"

def fetch_next_unhandled_request():
    """Fetch the next unhandled request from the noggin application and return a Request object."""
    try:
        response = requests.get(f"{NOGGIN_URL}/request/next-unhandled", headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
        if response.status_code == 200:
            data = response.json()
            # Create and return a Request object
            return Request(
                id=data.get('id'),
                timestamp=data.get('timestamp'),  # Adjust if necessary to convert to datetime
                source_ip=data.get('source_ip'),
                user_agent=data.get('user_agent'),
                method=data.get('method'),
                request_url=data.get('request_url'),
                request_raw=data.get('request_raw'),
                is_handled=data.get('is_handled')
            )
        else:
            print("Failed to fetch unhandled request:", response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print("Error fetching unhandled request:", e)
        return None

def process_request_data(request):
    """Process the fetched request data, now using a Request object."""
    if request.request_raw:
        # Assuming 'request_raw' is a JSON string, parse it
        payload = json.loads(request.request_raw)
        print("Processing payload:", payload)
        
        # Here, perform your specific processing of the payload
        # For example, processing data, making calculations, etc.
        import random

        for i in range(0, random.randint(1, 5)):
            print("Doing some heavy work...")
            time.sleep(random.randint(3,10))
        
        return True  # Return True if processing is successful
    return False  # Return False if there is no data to process


def mark_request_as_handled(request):
    headers = {
        'Authorization': f'Bearer {AUTH_TOKEN}',
        'Content-Type': 'application/json'  # Indicate JSON payload
    }
    payload = {
        'is_handled': 1  # Assuming setting `is_handled` to 1 marks it as handled
    }

    try:
        response = requests.put(f"{NOGGIN_URL}/request/{request.id}", json=payload, headers=headers)
        if response.status_code == 200:
            print(f"Request {request.id} marked as handled successfully.")
        else:
            # Attempt to extract and print a more descriptive error message
            try:
                error_message = response.json().get('message', 'No error message provided.')
            except ValueError:  # If response is not in JSON format
                error_message = response.text
            print(f"Failed to mark request {request.id} as handled: {response.status_code}, Error: {error_message}")
    except requests.exceptions.RequestException as e:
        print(f"Error marking request {request.id} as handled: {e}")
        
def fetch_and_process_next_unhandled_request():
    """Fetch and process the next unhandled request."""
    request = fetch_next_unhandled_request()
    if request and process_request_data(request):
        mark_request_as_handled(request)

# Schedule the fetch function to run every 5 seconds
schedule.every(5).seconds.do(fetch_and_process_next_unhandled_request)

if __name__ == "__main__":
    print("Starting mammoth application...")
    while True:
        schedule.run_pending()
        time.sleep(1)
