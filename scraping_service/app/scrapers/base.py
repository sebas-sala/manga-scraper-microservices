from abc import ABC
from rabbiteer import RabbitMQ

from app.config import Config
from app import redis_client

class Base(ABC):
    def __init__(self, queue: str):
        self.rabbitmq = RabbitMQ(
            host=Config.RABBITMQ_HOST, 
            username=Config.RABBITMQ_USER, 
            password=Config.RABBITMQ_PASS, 
            queue=queue,
        )
        self.url = Config.SCRAPE_MANGAS_URL
        self.redis_client = redis_client