import requests
import schedule
import time
import json

NOGGIN_URL = "http://127.0.0.1:5000"  # Adjust the URL/port as necessary

def fetch_and_process_next_unhandled_request():
    try:
        response = requests.get(f"{NOGGIN_URL}/request/next-unhandled")
        if response.status_code == 200:
            data = response.json()
            request_raw = data.get('request_raw')
            if request_raw:
                # Assuming 'request_raw' is a JSON string, parse it
                payload = json.loads(request_raw)
                print("Fetched and processing payload:", payload)
                
                # Here, perform your specific processing of the payload
                # For example, processing data, making calculations, etc.

                # After processing, remember to mark the request as handled in the 'noggin' application
                # This might involve sending a PUT request to update 'is_handled' to 1
                # Example: requests.put(f"{NOGGIN_URL}/request/{data['id']}/mark-handled")
                
            else:
                print("No unhandled requests found.")
        else:
            print("Failed to fetch unhandled request:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("Error fetching unhandled request:", e)

# Schedule the fetch function to run every 5 minutes
schedule.every(5).seconds.do(fetch_and_process_next_unhandled_request)

if __name__ == "__main__":
    print("Starting mammoth application...")
    while True:
        schedule.run_pending()
        time.sleep(1)
