import os 
from dotenv import load_dotenv

load_dotenv()

class Config:
    RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
    RABBITMQ_USER = os.environ.get("RABBITMQ_DEFAULT_USER", "guest")
    RABBITMQ_PASS = os.environ.get("RABBITMQ_DEFAULT_PASS", "guest")
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///db.sqlite3")
