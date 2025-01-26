import pytest
from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError

from app.services.tag_service import TagService
from app.models.tag import Tag

@pytest.fixture
def mock_session():
    with patch('app.services.tag_service.session') as mock_session:
        yield mock_session

class TestTagService:
    def test_create_tag_success(self, mock_session):
        service = TagService()
        service.create("test_tag")
        
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_create_bulk_tags(self, mock_session):
        service = TagService()
        service.create_bulk(["test_tag", "test_tag2"])
        
        mock_session.bulk_save_objects.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_create_bulk_tags_existing(self, mock_session):
        mock_session.query().filter().all.return_value = [Tag(name="test_tag")]
        
        service = TagService()
        service.create_bulk(["test_tag4", "test_tag2"])
        
        mock_session.bulk_save_objects.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_create_bulk_same_tags(self, mock_session):
        service = TagService()
        service.create_bulk(["test_tag", "test_tag"])
        
        mock_session.bulk_save_objects.assert_called()
        mock_session.commit.assert_called()

    def test_create_tag_error(self, mock_session):
        mock_session.commit.side_effect = SQLAlchemyError("Test error")
        
        service = TagService()
        service.create("test_tag")
        
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.rollback.assert_called_once()

    def test_on_message_valid_json(self):
        service = TagService()
        with patch.object(service, 'create_bulk') as mock_create:
            service.on_message('{"tags": ["test_tag"]}')
            mock_create.assert_called_once_with(["test_tag"])

    def test_on_message_invalid_json(self):
        service = TagService()
        with patch.object(service, 'create_bulk') as mock_create:
            service.on_message('invalid json')
            mock_create.assert_not_called()

    def test_on_message_missing_tag(self):
        service = TagService()
        with patch.object(service, 'create') as mock_create:
            service.on_message('{"other": "value"}')
            mock_create.assert_not_called()

    def test_on_message_dict_input(self):
        service = TagService()
        with patch.object(service, 'create_bulk') as mock_create:
            service.on_message({"tags": ["test_tag"]})
            mock_create.assert_called_once_with(["test_tag"])

    def test_create_validations(self):
        service = TagService()
        tag = Tag(name="test_tag")
        with patch.object(tag, 'validate_name') as mock_validate:
            service.create_validations(tag)
            mock_validate.assert_called_once_with("test_tag")
    
    def test_filter_existing_tags_empty_list(self, mock_session):
        service = TagService()
        result = service.filter_existing_tags([])
        assert result == []

    def test_filter_existing_tags_no_existing(self, mock_session):
        mock_session.query().filter().all.return_value = []
        
        service = TagService()
        result = service.filter_existing_tags(["tag1", "tag2"])
        
        assert result == ["tag1", "tag2"]
        assert mock_session.query.call_count == 2

    def test_filter_existing_tags_some_existing(self, mock_session):
        mock_session.query().filter().all.return_value = [Tag(name="tag1")]
        
        service = TagService()
        result = service.filter_existing_tags(["tag1", "tag2"])
        
        assert result == ["tag2"]
        assert mock_session.query.call_count == 2

    def test_filter_existing_tags_all_existing(self, mock_session):
        mock_session.query().filter().all.return_value = [
            Tag(name="tag1"),
            Tag(name="tag2")
        ]
        
        service = TagService()
        result = service.filter_existing_tags(["tag1", "tag2"])
        
        assert result == []
        assert mock_session.query.call_count == 2

    def test_filter_existing_tags_duplicates(self, mock_session):
        mock_session.query().filter().all.return_value = [Tag(name="tag1")]
        
        service = TagService()
        result = service.filter_existing_tags(["tag1", "tag1", "tag2"])
        
        assert result == ["tag2"]
        assert mock_session.query.call_count == 2
