from mammoth import Mammoth

NOGGIN_URL = "http://127.0.0.1:5000"
NUM_WORKERS = 2  # Adjust as needed.

app = Mammoth(noggin_url=NOGGIN_URL, workers=NUM_WORKERS)
print("Starting Mammoth application...")
app.run()