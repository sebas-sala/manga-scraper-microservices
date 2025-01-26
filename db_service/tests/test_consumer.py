import pytest
from unittest.mock import Mock, patch, MagicMock

from app.consumer import Consumer

@pytest.fixture
def mock_rabbitmq():
    with patch('app.consumer.RabbitMQ') as rabbitmq_mock:
        yield rabbitmq_mock

@pytest.fixture
def mock_tag_service():
    with patch('app.consumer.TagService') as tag_service_mock:
        yield tag_service_mock  

class TestConsumer:
    def test_initialize_rabbitmq(self, mock_rabbitmq):
        consumer = Consumer()
        assert consumer.tag_rabbitmq is not None

    def test_get_rabbitmq(self, mock_rabbitmq):
        mock_rabbitmq.return_value.host = 'rabbitmq'
        mock_rabbitmq.return_value.username = 'guest'
        mock_rabbitmq.return_value.password = 'guest'
        mock_rabbitmq.return_value.queue = 'test'

        consumer = Consumer()
        rabbitmq = consumer.get_rabbitmq('test')

        assert rabbitmq.host == 'rabbitmq'
        assert rabbitmq.username == 'guest'
        assert rabbitmq.password == 'guest'
        assert rabbitmq.queue == 'test' 

    def test_consumer_context_manager(self, mock_rabbitmq):
        """Test that consumer works as a context manager"""
        consumer = Consumer()
        
        with consumer as c:
          assert c == consumer
        
        assert consumer.tag_rabbitmq.close.called

    def test_start_consumers_handles_exception(self, mock_rabbitmq):
        """Test that start_consumers properly handles exceptions"""
        consumer = Consumer()
        
        consumer.start_tag_consumer = Mock(side_effect=Exception("Test error"))
        consumer.start_consumers()
        
        assert consumer.start_tag_consumer.called