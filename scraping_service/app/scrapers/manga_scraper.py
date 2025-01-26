import asyncio
import random
import logging
import aiohttp
import json
from bs4 import BeautifulSoup
from html_scrubber import clean_html

from app.scrapers.base import Base
from app.config import Config

LOGGER = logging.getLogger(__name__)

class MangaScraper(Base):

    def __init__(self):
        super().__init__('manga_queue')

        if not self.redis_client:
            LOGGER.error("Error connecting to Redis")
            return

        self.semaphore = asyncio.Semaphore(Config.MAX_CONCURRENT_REQUESTS)
        self.last_page = self.get_last_page()
        self.done = self.redis_client.get('mangas:done')
        self.ready = self.redis_client.get('mangas:ready')
        self.aio_session = None

    async def _create_aio_session(self):
        self.aio_session = aiohttp.ClientSession()

    async def _close_aio_session(self):
        if self.aio_session:
            await self.aio_session.close()

    def get_done(self) -> int:
        done = self.redis_client.get('mangas:done')
        return int(str(done)) if done else 0

    def set_done(self, done: int):
        self.done = done
        self.redis_client.set('mangas:done', done)

    def get_ready(self) -> int:
        ready = self.redis_client.get('mangas:ready')
        return int(str(ready)) if ready else 1
    
    def set_ready(self, ready: int):
        self.ready = ready
        self.redis_client.set('mangas:ready', ready)

    def get_last_page(self) -> int:
        last_page = self.redis_client.get('mangas:last_page')
        return int(str(last_page)) if last_page else 1

    def set_last_page(self, page: int):
        self.last_page = page
        self.redis_client.set('mangas:last_page', page)
        
    def increment_page(self):
        self.set_last_page(self.last_page + 1)
        
    def reset_all(self):
        self.set_last_page(1)
        self.set_done(0)
        self.set_ready(1)

    def reset(self):
        self.set_done(0)
        self.set_ready(1)

    async def fetch_page(self, page: int = 1):
        try:
            url = f"{self.url}/{page}"

            if not self.aio_session:
                await self._create_aio_session()
            if not self.aio_session:
                return None

            async with self.aio_session.get(url) as response:
                response.raise_for_status()
                return await response.text()
        except aiohttp.ClientError as e:
            LOGGER.error(f"Error al realizar la solicitud: {e}")
            return None
        
    async def fetch_manga(self, href: str):
        try:
            if not self.aio_session:
                await self._create_aio_session()
            if not self.aio_session:    
                return None

            async with self.aio_session.get(href) as response:
                response.raise_for_status()
                return await response.text()
        except aiohttp.ClientError as e:
            LOGGER.error(f"Error al realizar la solicitud: {e}")
            return None
        
    async def start_scraper(self):
        if self.get_ready() == 0:
            return

        response = await self.fetch_page(self.last_page)
        if not response: 
            self.increment_page()
            self.set_ready(1)
            return

        self.set_ready(0)

        soup = clean_html(response) 
        if isinstance(soup, str):
            soup = BeautifulSoup(soup, 'html.parser')
        mangas = soup.find_all('div', class_='doujin-col')

        if not mangas:
            self.set_done(1)
            return

        batches = [mangas[i:i + Config.MANGA_BATCH_SIZE] for i in range(0, len(mangas), Config.MANGA_BATCH_SIZE)]
        tasks = []

        for batch in batches:
            tasks.append(self.process_batch(batch))

        await asyncio.gather(*tasks)
        
        self.increment_page()
        self.set_ready(1)

    async def process_batch(self, batch):
        async with self.semaphore:
            LOGGER.info("Processing batch")

            for manga in batch:
                await asyncio.sleep(random.uniform(5, 20))

                try:
                    href = manga.find('a', class_='cover')['href']
                    if not href: continue
                    
                    manga_page = await self.fetch_manga(href)
                    if not manga_page: continue
                    
                    manga_soup = BeautifulSoup(manga_page, 'html.parser')

                    images = self.extract_images(manga_soup)
                    title = self.extract_title(manga_soup)

                    if not title or not images:
                        continue
                    
                    containers = self.extract_filter_containers(manga_soup, ['Artists', 'Tags', 'Uploaded', 'Groups'])

                    artists = self.extract_elements_from_container(containers.get('Artists'), 'span', 'filter-elem')
                    tags = self.extract_elements_from_container(containers.get('Tags'), 'span', 'filter-elem')
                    groups = self.extract_elements_from_container(containers.get('Groups'), 'span', 'filter-elem')
                    
                    cover = self.extract_cover(manga_soup)
                    uploaded_at = self.extract_uploaded_date(containers.get('Uploaded'))

                    self.send_manga_to_queue(
                        cover=cover, 
                        title=title, 
                        artists=artists, 
                        tags=tags,
                        uploaded_at=uploaded_at,
                        images=images,
                        groups= groups
                    )
                except Exception as e:
                    LOGGER.error(f"Error processing manga: {e}")
                    continue

    def send_manga_to_queue(
        self, 
        cover: str | None,
        groups: list[str], 
        title:str, 
        artists: list[str], 
        tags: list[str],
        uploaded_at: str | None,
        images: list[str]
    ):
        try: 
            message = json.dumps({
                'tags': tags,
                'title': title,
                'cover': cover,
                'groups': groups,
                'images': images,
                'artists': artists,
                "pages": len(images),
                'uploaded_at': uploaded_at,
            })
            self.rabbitmq.publish(message=message)
            LOGGER.info(f"Message sent to queue: {title}")
        except Exception as e:
            LOGGER.error(f'Error sending message to queue: {e}')

    def extract_cover(self, soup):
        cover_div = soup.find('div', id='main-cover')
        if not cover_div: return None

        return cover_div.find('img')['data-src']

    def extract_images(self, soup):
        image_divs = soup.find_all('div', class_='single-thumb-col')
        return [div.find('img')['data-src'] for div in image_divs]
        
    def extract_title(self, soup):
        h1 = soup.find('h1')
        if not h1: return None

        span = h1.find('span', class_='middle-title')
        if not span: return None

        return span.text
    
    def extract_filter_containers(self, soup, keys):
        containers = {}
        tag_containers = soup.find_all('div', class_='tag-container')
        for container in tag_containers:
            for key in keys:
                if key in container.text:
                    containers[key] = container
                    break
        return containers
    
    def extract_elements_from_container(self, container, tag, class_name):
        if not container:
            return []
        elements = container.find_all(tag, class_=class_name)
        return [elem.find('a').text.strip() for elem in elements if elem.find('a')]
    
    def extract_uploaded_date(self, container):
        try:
            return container.find('time')['datetime'] if container else None
        except Exception as e:
            LOGGER.error("Error extracting uploaded date: %s", e)
            return None