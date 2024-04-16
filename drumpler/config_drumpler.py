# Drumpler/config.py
import os
from dotenv import load_dotenv

load_dotenv('/home/sammy/drumpler/.env')  # Use an appropriate path

class ConfigDrumpler:
    AUTHORIZATION_KEY = os.getenv('AUTHORIZATION_KEY')
    DRUMPLER_HOST = os.getenv('DRUMPLER_HOST', "http://127.0.0.1")
    DRUMPLER_PORT = int(os.getenv('DRUMPLER_PORT', "5000"))
    DRUMPLER_DEBUG = bool(os.getenv('DRUMPLER_DEBUG', "True"))
    DATABASE_URI = os.getenv('DATABASE_URI')  # Ensure this is set in your .env for Drumpler

    @staticmethod
    def drumpler_url():
        if ConfigDrumpler.DRUMPLER_HOST.startswith("https") or ConfigDrumpler.DRUMPLER_PORT == 443:
            return f"{ConfigDrumpler.DRUMPLER_HOST}"
        else:
            return f"{ConfigDrumpler.DRUMPLER_HOST}:{ConfigDrumpler.DRUMPLER_PORT}"
