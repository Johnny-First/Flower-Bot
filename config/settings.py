import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    DEEP_KEY = os.getenv("DEEP_KEY")
    PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN")

settings = Settings() 
        