import os
from dotenv import load_dotenv

load_dotenv('/home/sammy/drumpler/.env')  # TODO: DO NOT HARDCODE ENV FILE

AUTHORIZATION_KEY = os.getenv('AUTHORIZATION_KEY')

# Load environment variables
DRUMPLER_HOST = os.getenv('DRUMPLER_HOST', "http://127.0.0.1")
DRUMPLER_PORT = int(os.getenv('DRUMPLER_PORT', "5000"))

if DRUMPLER_HOST.startswith("https") or DRUMPLER_PORT==443:
    DRUMPLER_URL = f"{DRUMPLER_HOST}"  # Adjust the URL/port as necessary
else:
    DRUMPLER_URL = f"{DRUMPLER_HOST}:{DRUMPLER_PORT}"  # Adjust the URL/port as necessary

DRUMPLER_DEBUG = bool(os.getenv('DRUMPLER_DEBUG', "True"))

DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'