import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from request import Request


class Mammoth:
    def __init__(self, noggin_url, auth_token, workers=None):
        self.noggin_url = noggin_url
        self.auth_token = auth_token
        self.workers = workers if workers is not None else multiprocessing.cpu_count()

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
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            while True:
                futures = [executor.submit(self.fetch_and_process_next_unhandled_request) for _ in range(self.workers)]
                for future in futures:
                    future.result()  # Waits for the thread to complete and handles exceptions if any

    def fetch_and_process_next_unhandled_request(self):
        request = self.fetch_next_unhandled_request()
        if request:
            process = self.process_request_data(request)

            if process:
                request.mark_as_handled()

if __name__ == "__main__":
    NOGGIN_URL = "http://127.0.0.1:5000"  # Adjust the URL/port as necessary
    AUTH_TOKEN = "YourAuthorizationKeyHere"  # Your actual authorization token
    NUM_WORKERS = 2

    mammoth_app = Mammoth(NOGGIN_URL, AUTH_TOKEN, NUM_WORKERS)
    print("Starting Mammoth application...")
    mammoth_app.run()
