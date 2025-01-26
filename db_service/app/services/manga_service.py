"""Manga service module."""

import logging
import json

from app.db import session
from app.models import Manga

from app.services import TagService, ArtistService, GroupService, Base

LOGGER = logging.getLogger(__name__)

class MangaService(Base):
    """Service class for handling mangas"""
    def __init__(self, db_session=None) -> None:
        self.session = db_session or session
        self.tag_service = TagService(db_session=self.session)
        self.artist_service = ArtistService(db_session=self.session)
        self.group_service = GroupService(db_session=self.session)

    def get_by_title(self, title: str) -> Manga | None:
        """Get a manga by title"""
        return self.session.query(Manga).filter(Manga.title == title).first()

    def create(
        self,
        title:str,
        cover:str,
        pages:int,
        uploaded_at:str,
        images:list[str],
        artists:list[str] = [],
        groups:list[str] = [],
        tags:list[str] = [],
    ) -> Manga:
        """Save a new manga"""

        if not images:
            raise ValueError("Manga must have at least one image")

        related_tags = self.tag_service.get_or_create_many(tags)
        related_groups = self.group_service.get_or_create_many(groups)
        related_artists = self.artist_service.get_or_create_many(artists)

        manga = Manga(
            title=title,
            cover=cover,
            pages=pages,
            images=images,
            uploaded_at=uploaded_at,
            tags=related_tags,
            groups=related_groups,
            artists=related_artists,
        )

        try:
            self.session.add(manga)
            self.session.commit()

            LOGGER.info("Manga saved: %s", manga.title)
            return manga
        except Exception as e:
            LOGGER.error("Error saving manga %s: %s", manga.title, e)
            self.session.rollback()
            raise

    def on_message(self, body: dict) -> None:
        """Handle incoming messages"""
        body = self.format_body(body)
        self.validate_income_message(body)
        try:
            manga_data = {
                "title": str(body.get("title", "")),
                "pages": int(body.get("pages", 0)),
                "cover": str(body.get("cover", "")),
                "groups": [str(g) for g in body.get("groups", [])],
                "images": [str(i) for i in body.get("images", [])],
                "artists": [str(a) for a in body.get("artists", [])],
                "uploaded_at": str(body.get("uploaded_at", "")),
                "tags": [str(t) for t in body.get("tags", [])],
            }

            self.create(**manga_data)

        except json.JSONDecodeError:
            LOGGER.error("Invalid JSON message: %s", body)
        except Exception as e:
            LOGGER.error("Unexpected error while processing message: %s", e)

    def format_body(self, body):
        """Format incoming message body"""
        if isinstance(body, str):
            return json.loads(body)
        return body

    def validate_income_message(self, body):
        """Validate incoming message"""

        if not isinstance(body, dict):
            LOGGER.warning("Invalid message type: %s", type(body))
            raise ValueError("Invalid message type")
        
        required_fields = ["title", "images"]
        missing_fields = [field for field in required_fields if field not in body]

        if missing_fields:
            LOGGER.warning("Missing fields in message: %s", missing_fields)
            raise ValueError(f"Missing fields in message: {missing_fields}")

        pages = body.get("pages")
        if pages is None:
            LOGGER.warning("Missing pages field in message")
            raise ValueError("Missing pages field in message")
