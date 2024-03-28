import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, Future
import multiprocessing
from request import Request
import keyboard  # Import the keyboard package
import threading  # Import the threading module
import os


class Mammoth:
    def __init__(self, noggin_url, workers=None):
        self.noggin_url = noggin_url
        self.auth_key = os.getenv('AUTHORIZATION_KEY', 'default_key')  # Default value if not set
        self.workers = workers if workers is not None else multiprocessing.cpu_count()
        self.stop_signal = False  # A flag to signal workers to stop

    def fetch_next_unhandled_request(self):
        headers = {"Authorization": f"Bearer {self.auth_key}"}
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
            #print(f"Processing payload: {payload}")
            # Simulate some work
            # Simulate some work
            import random

            thread_id = threading.get_ident()  # Get the current thread's identifier

            for i in range(random.randint(1, 5)):
                print(f"Request: {request.id}\tThread:{thread_id}\tDoing some heavy work...")
                time.sleep(random.randint(1, 5))
            
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

        def worker():
            while not self.stop_signal:
                request = self.fetch_next_unhandled_request()
                if request:
                    self.process_request_data(request)
                    request.mark_as_handled()

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            # Start the stop check in a separate thread
            executor.submit(stop_check)
            
            # Launch a worker task for each worker
            workers = [executor.submit(worker) for _ in range(self.workers)]
            
            # Wait for all workers to complete (which only happens when stop_signal is True)
            for future in workers:
                try:
                    future.result()  # Waits for the thread to complete and handles exceptions if any
                except KeyboardInterrupt:
                    self.stop_signal = True
                except Exception as e:
                    print(f"Error in worker thread: {e}")

if __name__ == "__main__":
    NOGGIN_URL = "http://127.0.0.1:5000"
    NUM_WORKERS = 2

    mammoth_app = Mammoth(NOGGIN_URL, NUM_WORKERS)
    print("Starting Mammoth application... Press 'q' to stop.")
    mammoth_app.run()
