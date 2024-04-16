# Mammoth/config.py
import os
from dotenv import load_dotenv

load_dotenv('/home/sammy/drumpler/.env')  # Use an appropriate path

class ConfigMammoth:
    AUTHORIZATION_KEY = os.getenv('AUTHORIZATION_KEY')
    DRUMPLER_URL = os.getenv('DRUMPLER_URL')  # Ensure this is complete including the port if needed
