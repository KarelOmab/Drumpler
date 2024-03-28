import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, Future
import multiprocessing
from request import Request
import keyboard  # Import the keyboard package

class Mammoth:
    def __init__(self, noggin_url, auth_token, workers=None):
        self.noggin_url = noggin_url
        self.auth_token = auth_token
        self.workers = workers if workers is not None else multiprocessing.cpu_count()
        self.stop_signal = False  # A flag to signal workers to stop

    def fetch_next_unhandled_request(self):
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        try:
            response = requests.get(f"{self.noggin_url}/request/next-unhandled", headers=headers)
            if response.status_code == 200:
                data = response.json()
                return Request(
                    id=data.get('id'),
                    timestamp=data.get('timestamp'),  
                    source_ip=data.get('source_ip'),
                    user_agent=data.get('user_agent'),
                    method=data.get('method'),
                    request_url=data.get('request_url'),
                    request_raw=data.get('request_raw'),
                    is_handled=data.get('is_handled')
                )
            else:
                print("Failed to fetch unhandled request:", response.status_code)
                time.sleep(5)
                return None
        except requests.exceptions.RequestException as e:
            print("Error fetching unhandled request:", e)
            return None

    def process_request_data(self, request):
        if request and request.request_raw:
            payload = json.loads(request.request_raw)
            print(f"Processing payload: {payload}")
            # Simulate some work
            import random

            for i in range(0, random.randint(1, 5)):
                print(f"{request.id} Doing some heavy work...")
                time.sleep(1)
            
            return True
        return False

    def run(self):
        def stop_check():
            while True:
                if keyboard.is_pressed('q'):  # If 'q' is pressed
                    print("\nStopping all workers...")
                    self.stop_signal = True  # Set the stop signal
                    break
                time.sleep(0.1)  # Check every 100ms

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            # Start the stop check in a separate thread
            stop_thread = executor.submit(stop_check)
            
            # Start processing jobs until stop signal is received
            while not self.stop_signal:
                futures = [executor.submit(self.fetch_and_process_next_unhandled_request) for _ in range(self.workers)]
                for future in futures:
                    if self.stop_signal:
                        break  # Break the loop if stop signal is received
                    try:
                        future.result(timeout=10)  # Waits for the thread to complete and handles exceptions if any
                    except KeyboardInterrupt:
                        self.stop_signal = True
                        break
                    except Future.TimeoutError:
                        # Handle timeout if a future doesn't complete within the specified time
                        continue

            # Cancel all futures if they're still running
            for future in futures:
                future.cancel()
            
            # Wait for the stop check thread to complete
            stop_thread.result()

    def fetch_and_process_next_unhandled_request(self):
        if self.stop_signal:  # Check if stop signal is received before starting new work
            return
        
        request = self.fetch_next_unhandled_request()
        if request:
            process = self.process_request_data(request)

            if process:
                request.mark_as_handled()

if __name__ == "__main__":
    NOGGIN_URL = "http://127.0.0.1:5000"
    AUTH_TOKEN = "YourAuthorizationKeyHere"
    NUM_WORKERS = 2

    mammoth_app = Mammoth(NOGGIN_URL, AUTH_TOKEN, NUM_WORKERS)
    print("Starting Mammoth application... Press 'q' to stop.")
    mammoth_app.run()
