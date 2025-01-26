import os 
from dotenv import load_dotenv

load_dotenv()

class Config:
    RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
    RABBITMQ_USER = os.environ.get("RABBITMQ_DEFAULT_USER", "guest")
    RABBITMQ_PASS = os.environ.get("RABBITMQ_DEFAULT_PASS", "guest")
    SCRAPE_MANGAS_URL = os.environ.get("SCRAPE_MANGAS_URL", "")
    SCRAPE_INTERVAL = int(os.environ.get("SCRAPE_INTERVAL", 15))
    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
    MAX_CONCURRENT_REQUESTS = int(os.environ.get("MAX_CONCURRENT_REQUESTS", 5))
    MANGA_BATCH_SIZE = int(os.environ.get("MANGA_BATCH_SIZE", 5))