import json
import requests
import logging
from bs4 import BeautifulSoup

from app.scrapers.base import Base

LOGGER = logging.getLogger(__name__)

class TagScraper(Base):
    MIN_QTY = 1000

    def __init__(self):
        super().__init__('tags_queue')

        if not self.redis_client: 
            LOGGER.error("Error connecting to Redis")
            return
        
        self.done = self.redis_client.get('tags:done')

    def reset_page(self):
        self.set_last_page(1)
        self.set_done(0)

    def set_last_page(self, page: int):
        self.redis_client.set('tags:last_page', page)

    def get_last_page(self) -> int:
        last_page = self.redis_client.get('tags:last_page')

        if last_page:    
            return int(str(last_page))
        else:
            return 1 

    def set_done(self, done: int):
        self.redis_client.set('tags:done', done)
        
    def api_fetch(self, page: int = 1):
        try:
            response = requests.get(self.url + '/tags', params={'page': page})
            response.raise_for_status() 
            return response
        except requests.exceptions.RequestException as e:
            LOGGER.error(f"Error al realizar la solicitud: {e}")
            return None
        
    def send_tags_to_queue(self, tags: list[str]):
        try: 
            message = json.dumps({'tags': tags})
            self.rabbitmq.publish(message=message)
        except Exception as e:
            LOGGER.error(f'Error sending message to queue: {e}')

    def start_scraper(self) -> None:
        if self.done == 1:
            LOGGER.info("Tag scraping is done") 
            return
        
        page = self.get_last_page()
        response = self.api_fetch(page)
        if not response or not response.ok: return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        tags = soup.find_all('a', class_='name')

        if not tags:
            LOGGER.error(f"No tags found on page {page}")
            self.set_done(1)
            return

        filtered_tags = self.filter_tags_by_quantity(tags)

        self.send_tags_to_queue(filtered_tags)  
        self.set_last_page(page + 1)
      
    def filter_tags_by_quantity(self, tags) -> list[str]:
        return [
            tag.text.strip()
            for tag in tags
            if self.transform_quantity(tag.get('data-qty', '0')) > self.MIN_QTY
        ]

    def transform_quantity(self, quantity: str):
        if not quantity:
            return 0 

        lower_case_qty = quantity.lower()
        multiplier = 1

        if lower_case_qty.endswith('k'):
            multiplier = 1000

        number_part = int(lower_case_qty.replace('k', ''))
        return number_part * multiplier