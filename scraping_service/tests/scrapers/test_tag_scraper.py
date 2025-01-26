import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from app.scrapers.tag_scraper import TagScraper

@pytest.fixture
def tag_scraper():
    with patch('app.scrapers.base.RabbitMQ') as mock_rabbit, patch('app.scrapers.tag_scraper.redis_client', new_callable=AsyncMock) as mock_redis:
        mock_redis.get.return_value = b'3'
        mock_redis.set.return_value = None
        tag_scraper = TagScraper()
        yield tag_scraper

class TestTagScraper:
    # def test_api_fetch(self, tag_scraper):
    #     response = tag_scraper.api_fetch(2)
    #     assert response is not None

    def test_filter_tags_by_quantity(self, tag_scraper):
        tags = [
            MagicMock(text='tag1', get=lambda x, default=None: '1k' if x == 'data-qty' else default),
            MagicMock(text='tag2', get=lambda x, default=None: '4k' if x == 'data-qty' else default),
            MagicMock(text='tag3', get=lambda x, default=None: '2k' if x == 'data-qty' else default),
        ]
        
        filtered_tags = tag_scraper.filter_tags_by_quantity(tags)
        assert filtered_tags == ['tag2', 'tag3']

    def test_transform_quantity(self, tag_scraper):
        assert tag_scraper.transform_quantity('1k') == 1000
        assert tag_scraper.transform_quantity('999') == 999
        assert tag_scraper.transform_quantity('2k') == 2000
        assert tag_scraper.transform_quantity('') == 0

    def test_send_tags_to_queue(self, tag_scraper):
        tag_scraper.send_tags_to_queue(['tag1', 'tag2'])
        assert tag_scraper.rabbitmq.publish.called

    @pytest.mark.asyncio
    async def test_last_page_found(self, tag_scraper):
        last_page = await tag_scraper.get_last_page()
        assert last_page == 3

    def test_set_last_page(self, tag_scraper):
        tag_scraper.set_last_page(5)
        assert tag_scraper.redis_client.set.called