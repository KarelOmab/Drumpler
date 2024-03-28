import requests
import schedule
import time
import json

NOGGIN_URL = "http://127.0.0.1:5000"  # Adjust the URL/port as necessary
AUTH_TOKEN = "YourAuthorizationKeyHere"

def fetch_next_unhandled_request():
    """Fetch the next unhandled request from the noggin application."""
    try:
        response = requests.get(f"{NOGGIN_URL}/request/next-unhandled")
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to fetch unhandled request:", response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print("Error fetching unhandled request:", e)
        return None

def process_request_data(data):
    """Process the fetched request data."""
    request_raw = data.get('request_raw')
    if request_raw:
        # Assuming 'request_raw' is a JSON string, parse it
        payload = json.loads(request_raw)
        print("Processing payload:", payload)
        
        # Here, perform your specific processing of the payload
        # For example, processing data, making calculations, etc.
        
        # Return True if processing is successful
        return True
    return False

def mark_request_as_handled(request_id):
    headers = {
        'Authorization': f'Bearer {AUTH_TOKEN}',
        'Content-Type': 'application/json'  # Indicate JSON payload
    }
    payload = {
        'is_handled': 1  # Assuming setting `is_handled` to 1 marks it as handled
    }

    try:
        response = requests.put(f"{NOGGIN_URL}/request/{request_id}", json=payload, headers=headers)
        if response.status_code == 200:
            print(f"Request {request_id} marked as handled successfully.")
        else:
            # Attempt to extract and print a more descriptive error message
            try:
                error_message = response.json().get('message', 'No error message provided.')
            except ValueError:  # If response is not in JSON format
                error_message = response.text
            print(f"Failed to mark request {request_id} as handled: {response.status_code}, Error: {error_message}")
    except requests.exceptions.RequestException as e:
        print(f"Error marking request {request_id} as handled: {e}")
        
def fetch_and_process_next_unhandled_request():
    """Fetch and process the next unhandled request."""
    data = fetch_next_unhandled_request()
    print("data", data)
    if data and 'id' in data and process_request_data(data):
        print(f"mark_request_as_handled: {data['id']}")
        mark_request_as_handled(data['id'])

# Schedule the fetch function to run every 5 seconds
schedule.every(5).seconds.do(fetch_and_process_next_unhandled_request)

if __name__ == "__main__":
    print("Starting mammoth application...")
    while True:
        schedule.run_pending()
        time.sleep(1)
