"""
Service class for handling tags
"""

import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import session
from app.models import Artist
from app.services.base_service import Base

LOGGER = logging.getLogger(__name__)

class ArtistService(Base):
    """Service class for handling artists"""

    def __init__(self, db_session: Session | None = None) -> None:
        self.session = db_session or session
        self.artist_query = self.session.query(Artist)

    def get_by_name(self, name: str) -> Artist | None:
        """Get a tag by name"""
        return self.artist_query.filter(Artist.name == name).first()
    
    def get_by_names(self, names: list[str]) -> list[Artist]:
        """Get tags by names"""
        self.artist_query.filter(Artist.name.in_(names)).all()    
        return self.artist_query.filter(Artist.name.in_(names)).all()    

    def create(self, name:str):
        """Create a new tag"""
        tag = Artist(name=name)

        try:
            self.session.add(tag)
            self.session.commit()
        except SQLAlchemyError as e:
            LOGGER.error("Error saving tag %s: %s", tag.name, e)
            self.session.rollback()

    def get_or_create_many(self, names: list[str]) -> list[Artist]:
        """Get or create a list of tags"""

        if not names:
            return []
        
        existing_artists = self.get_by_names(names)
        existing_names = {artist.name for artist in existing_artists}

        new_artists_names = list(set(names) - existing_names)

        if not new_artists_names:
            return existing_artists

        try:
            new_artists = self.create_bulk(new_artists_names)
            return existing_artists + new_artists
        except SQLAlchemyError as e:
            LOGGER.error("Error saving tags: %s", e)
            return existing_artists

    def create_bulk(self, names: list[str]) -> list[Artist]:
        """Create a list of tags"""
        if not names:
            return []

        artist_objects = [Artist(name=name) for name in names]

        try:
            self.session.add_all(artist_objects)
            self.session.commit()
            return artist_objects
        except SQLAlchemyError as e:
            LOGGER.error("Error saving tags: %s", e)
            return []
