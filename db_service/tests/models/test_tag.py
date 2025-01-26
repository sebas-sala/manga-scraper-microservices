import pytest
from unittest.mock import patch, MagicMock

from app.models.tag import Tag

class TestTag:      
    def test_tag_creation_with_default_values(self):
        tag = Tag()

        assert tag.name is None

    def test_tag_creation_with_values(self):
        tag = Tag(name="test_tag", quantity=5)
        assert str(tag.name) == "test_tag"
        assert tag.quantity == 5

    def test_validate_name_with_empty_string(self):
        tag = Tag()
        with pytest.raises(ValueError) as exc_info:
            tag.validate_name("")
        assert str(exc_info.value) == "Invalid tag name"

    def test_validate_name_with_none(self):
        tag = Tag()
        with pytest.raises(ValueError) as exc_info:
            tag.validate_name(None)
        assert str(exc_info.value) == "Invalid tag name"

    def test_validate_name_too_long(self):
        tag = Tag()
        long_name = "a" * 101
        with pytest.raises(ValueError) as exc_info:
            tag.validate_name(long_name)
        assert str(exc_info.value) == "Tag name too long"

    def test_validate_name_valid(self):
        tag = Tag()
        tag.validate_name("valid_tag")