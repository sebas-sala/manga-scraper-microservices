import pytest

from app.models import Base
from tests import Session, engine
from dateutil.parser import isoparse
from datetime import timezone

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = Session()
    
    try:
        yield db
    finally:
        db.rollback()

        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())  

        db.commit()
        db.close()

@pytest.fixture
def manga_service(db_session):
    from app.services.manga_service import MangaService
    service = MangaService(db_session=db_session)
    return service

class TestMangaService:
    def test_save_manga(self, manga_service):
        test_data = {
            "title": "Test Manga",
            "cover": "thumbnail.jpg",
            "pages": 10,
            "uploaded_at": "2025-01-26T05:48:04+00:00",
            "images": ["page1.jpg", "page2.jpg"]
        }
     
        result = manga_service.create(**test_data)

        assert result.title == test_data["title"]
        assert result.cover == test_data["cover"]
        assert result.pages == test_data["pages"]
        assert result.uploaded_at.replace(tzinfo=timezone.utc) == isoparse(test_data["uploaded_at"])
        assert result.images == test_data["images"]

    def test_create_manga_with_relations(self, manga_service):
        test_data = {
            "title": "Test Manga",
            "cover": "thumbnail.jpg",
            "pages": 10,
            "uploaded_at": "2023-01-01",
            "images": ["page1.jpg", "page2.jpg"],
            "artists": ["Artist 1", "Artist 2"],
            "groups": ["Group 1", "Group 2"],
            "tags": ["Tag 1", "Tag 2", "Tag 1"]
        }
        
        result = manga_service.create(**test_data)
        
        assert result.title == test_data["title"]
        assert result.cover == test_data["cover"]
        assert result.pages == test_data["pages"]
        assert result.images == test_data["images"]

        assert len(result.artists) == 2
        assert len(result.groups) == 2
        assert len(result.tags) == 2

    def test_create_manga_with_no_images(self, manga_service):
        test_data = {
            "title": "Test Manga",
            "cover": "thumbnail.jpg",
            "pages": 10,
            "uploaded_at": "2023-01-01",
            "images": []
        }

        with pytest.raises(ValueError):
            manga_service.create(**test_data)

    def test_get_by_title(self, manga_service):
        test_data = {
            "title": "Test Manga",
            "cover": "thumbnail.jpg",
            "pages": 10,
            "uploaded_at": "2023-01-01",
            "images": ["page1.jpg", "page2.jpg"]
        }

        manga_service.create(**test_data)
        result = manga_service.get_by_title(test_data["title"])

        assert result.title == test_data["title"]
        assert result.cover == test_data["cover"]
        assert result.pages == test_data["pages"]
        assert result.images == test_data["images"]

    def test_get_by_title_not_found(self, manga_service):
        result = manga_service.get_by_title("Test Manga")

        assert result is None   

    def test_on_message(self, manga_service):
        test_data = ""
        import json
        parsed_data = json.loads(test_data)

        manga_service.on_message(test_data)
        result = manga_service.get_by_title(parsed_data["title"])
        
        assert result.title == parsed_data["title"]
        assert result.cover == parsed_data["cover"]
        assert result.pages == parsed_data["pages"]
        assert result.images == parsed_data["images"]

        assert len(result.artists) == len(parsed_data["artists"])
        assert len(result.groups) == len(parsed_data["groups"])
        assert len(result.tags) == len(parsed_data["tags"])

    def test_on_message_with_invalid_data(self, manga_service):
        with pytest.raises(ValueError):
            manga_service.on_message({})