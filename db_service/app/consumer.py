import logging
import threading
import logging.config
from typing import Callable
from rabbiteer import RabbitMQ

from app.config import Config
from app.services import TagService, MangaService

LOGGER = logging.getLogger(__name__)

class Consumer:
    TAG = 'tags_queue'
    MANGA = 'manga_queue'

    def __init__(self):
        self.tag_service = TagService()
        self.manga_service = MangaService()
        self.initialize_rabbitmq()

    def initialize_rabbitmq(self):
        """Initialize RabbitMQ instances"""
        self.tag_rabbitmq = self.get_rabbitmq(self.TAG)
        self.manga_rabbitmq = self.get_rabbitmq(self.MANGA)

    def get_rabbitmq(self, queue: str) -> RabbitMQ:
        """Get a RabbitMQ instance for the given queue"""
        return RabbitMQ(
            host=Config.RABBITMQ_HOST,
            username=Config.RABBITMQ_USER,
            password=Config.RABBITMQ_PASS,
            queue=queue
        )
    
    def start_consumers(self):
        """Start all consumers"""
        try: 
            # self.start_tag_consumer()
            self.start_manga_consumer()
        except Exception as e:
            LOGGER.error(f"Error starting consumers: {e}")

    def start_manga_consumer(self):
        """Start the manga consumer"""
        thread = threading.Thread(target=self.consume_messages, args=(self.manga_rabbitmq, self.manga_service.on_message), daemon=True)
        thread.start()
        thread.join()

    def start_tag_consumer(self):
        """Start the tag consumer"""
        thread = threading.Thread(target=self.consume_messages, args=(self.tag_rabbitmq, self.tag_service.on_message), daemon=True)
        thread.start()
        thread.join()

    def consume_messages(self, rabbitmq: RabbitMQ, callback: Callable):
        with rabbitmq as rmq:
            rmq.consume(callback)
    
    def __enter__(self):        
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.tag_rabbitmq.close()
        LOGGER.info("RabbitMQ connections closed")