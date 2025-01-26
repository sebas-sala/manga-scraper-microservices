import asyncio

from app.scrapers import TagScraper, MangaScraper
from app.config import Config

import logging
LOGGER = logging.getLogger(__name__)

class Cron:
    def __init__(self):
        pass

    @staticmethod
    async def run_manga_scraper():
        manga_scraper = MangaScraper()
        manga_scraper.reset()
        # manga_scraper.reset_all()

        while True:
            mangas_done = manga_scraper.get_done()
            if mangas_done == 1: 
                break

            mangas_ready = manga_scraper.get_ready()
            if mangas_ready == 0:
                await asyncio.sleep(Config.SCRAPE_INTERVAL)
                continue
                
            await manga_scraper.start_scraper()
            await asyncio.sleep(Config.SCRAPE_INTERVAL)

    @staticmethod
    async def run_tag_scraper():
        tag_scraper = TagScraper()
        tag_scraper.reset_page()

        while True:
            tags_done = tag_scraper.get_last_page()
            
            if tags_done is None or tags_done == 0:
                await asyncio.to_thread(tag_scraper.start_scraper)
                await asyncio.sleep(Config.SCRAPE_INTERVAL)
            else:
                break
        
    @staticmethod
    async def run_schedule():
        await Cron.run_manga_scraper()

        # Uncomment this line to run the tag scraper
        # await Cron.run_tag_scraper()


    @staticmethod 
    async def run():
        await Cron.run_schedule()