from mammoth import Mammoth
import threading
import time
import signal
from constants import NOGGIN_URL, MAMMOTH_WORKERS

def custom_process_function(session, request, job_id):
    # Custom logic for processing a request
    print(f"Processing request {request.id} with job_id {job_id}")
    thread_id = threading.get_ident()

    # Simulate some work
    import random
    for _ in range(random.randint(1, 5)):
        print(f"Request: {request.id}\tThread:{thread_id}\tDoing some heavy work...")
        time.sleep(random.randint(1, 5))

    return True

# Initialize Mammoth

app = Mammoth(process_request_data=custom_process_function, noggin_url=NOGGIN_URL, workers=MAMMOTH_WORKERS)

def signal_handler(sig, frame):
    print("CTRL+C pressed! Stopping Mammoth application...")
    app.stop()

if __name__ == "__main__":
    # Register SIGINT handler
    signal.signal(signal.SIGINT, signal_handler)

    print("Starting Mammoth application... Press CTRL+C to stop.")
    app.run()
