import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    DEEP_KEY = os.getenv("DEEP_KEY")
    PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN")
    CHANNEL_URL = os.getenv("CHANNEL_URL")
    API_KEY = os.getenv("API_KEY")
    ADMIN_IDS = os.getenv("ADMIN_IDS", "")

settings = Settings() 
        