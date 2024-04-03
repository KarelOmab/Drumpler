import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

AUTHORIZATION_KEY = os.getenv('AUTHORIZATION_KEY')

# Load environment variables
DRUMPLER_HOST = "http://127.0.0.1"
DRUMPLER_PORT = 5000  # Adjust the URL/port as necessary
DRUMPLER_URL = f"{DRUMPLER_HOST}:{DRUMPLER_PORT}"  # Adjust the URL/port as necessary
DRUMPLER_DEBUG = True
MAMMOTH_WORKERS = 1

DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
