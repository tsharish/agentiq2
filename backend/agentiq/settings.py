import os
from dotenv import load_dotenv

load_dotenv()

ORIGIN = os.getenv("ORIGIN")
BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL")
APP_USERNAME = os.getenv("APP_USERNAME")
APP_PASSWORD = os.getenv("APP_PASSWORD")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
