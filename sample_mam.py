from mammoth import Mammoth
import threading
import time
import signal
from constants import NOGGIN_URL, MAMMOTH_WORKERS

def custom_process_function(session, request, job_id):
    # Custom logic for processing a request
    thread_id = threading.get_ident()
    
    # Simulate some work
    import random
    for _ in range(random.randint(1, 5)):
        print(f"Request: {request.id}\tThread:{thread_id}\tDoing some heavy work...")
        mammoth.insert_event(session, job_id, f"Request: {request.id}\tThread:{thread_id}\tDoing some heavy work...")
        time.sleep(random.randint(1, 5))

    return True




# Initialize Mammoth

mammoth = Mammoth(process_request_data=custom_process_function, noggin_url=NOGGIN_URL, workers=MAMMOTH_WORKERS)

def signal_handler(sig, frame):
    print("CTRL+C pressed! Stopping Mammoth...")
    mammoth.stop()

if __name__ == "__main__":
    # Register SIGINT handler
    signal.signal(signal.SIGINT, signal_handler)

    print("Starting Mammoth... Press CTRL+C to stop.")
    mammoth.run()
