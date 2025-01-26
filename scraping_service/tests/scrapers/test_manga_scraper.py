import pytest
import requests
from unittest.mock import patch, MagicMock

from app.scrapers.manga_scraper import MangaScraper

import logging

LOGGER = logging.getLogger(__name__)

@pytest.fixture
def manga_scraper():
    with patch('app.scrapers.base.RabbitMQ') as mock_rabbit, patch('app.scrapers.base.redis_client') as mock_redis:
        mock_redis.get.return_value = '5'

        manga_scraper = MangaScraper()
        yield manga_scraper

@pytest.mark.asyncio
class TestMangaScraper:        
    def test_set_last_tag(self, manga_scraper):
        manga_scraper.set_last_tag(5)
        assert manga_scraper.last_tag == 5
        manga_scraper.redis_client.set.assert_called_once_with('mangas:last_tag', 5)
        
    def test_set_last_page(self, manga_scraper):
        manga_scraper.set_last_page(10)
        assert manga_scraper.last_page == 10
        manga_scraper.redis_client.set.assert_called_once_with('mangas:last_page', 10)

    def test_get_last_tag(self, manga_scraper):
        manga_scraper.redis_client.get.return_value = '5'
        result = manga_scraper.get_last_tag()
        assert result == '5'
        manga_scraper.redis_client.get.assert_called_with('mangas:last_tag')

    def test_get_last_tag_none(self, manga_scraper):
        manga_scraper.redis_client.get.return_value = None
        result = manga_scraper.get_last_tag()
        assert result is None
        manga_scraper.redis_client.get.assert_called_with('mangas:last_tag')

    def test_get_last_page(self, manga_scraper):
        manga_scraper.redis_client.get.return_value = '10'
        result = manga_scraper.get_last_page()
        assert result == 10
        manga_scraper.redis_client.get.assert_called_with('mangas:last_page')

    def test_get_last_page_default(self, manga_scraper):
        manga_scraper.redis_client.get.return_value = None
        result = manga_scraper.get_last_page()
        assert result == 1
        manga_scraper.redis_client.get.assert_called_with('mangas:last_page')

    @patch('requests.get')
    def test_api_fetch_success(self, mock_get, manga_scraper):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_get.return_value = mock_response
        
        result = manga_scraper.api_fetch(1)
        mock_get.assert_called_once_with(f'{manga_scraper.url}/mangas?page=1')
        assert result == mock_response

    @patch('requests.get')
    def test_api_fetch_failure(self, mock_get, manga_scraper):
        mock_get.side_effect = requests.exceptions.RequestException()
        result = manga_scraper.api_fetch(1)
        assert result is None

    def test_start_scraper_failed_request(self, manga_scraper):
        with patch.object(manga_scraper, 'api_fetch') as mock_fetch:
            mock_fetch.return_value = None
            manga_scraper.start_scraper()
            mock_fetch.assert_called_once_with(manga_scraper.last_page)

    async def test_start_scraper(self, manga_scraper):   
        manga_scraper.last_page = 1  
        result = await manga_scraper.start_scraper()