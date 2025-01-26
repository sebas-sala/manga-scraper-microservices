"""
Service class for handling tags
"""

import logging
import json
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import session
from app.models import Tag
from app.services import Base

LOGGER = logging.getLogger(__name__)

class TagService(Base):
    """Service class for handling tags"""

    def __init__(self, db_session: Session | None = None):
        self.session = db_session or session

    def get_by_name(self, name: str) -> Tag | None:
        """Get a tag by name"""
        return self.session.query(Tag).filter(Tag.name == name).first()
    
    def get_by_names(self, names: list[str]) -> list[Tag]:
        """Get tags by names"""
        return self.session.query(Tag).filter(Tag.name.in_(names)).all()    
    
    def get_or_create_many(self, names: list[str]) -> list[Tag]:
        """Get or create a list of tags"""
        if not names:
            return []

        existing_tags = self.get_by_names(names)
        existing_names = {tag.name for tag in existing_tags}

        new_tags_names = list(set(names) - existing_names)

        if not new_tags_names:
            return existing_tags

        try:
            new_tags = self.create_bulk(new_tags_names)
            return existing_tags + new_tags
        except SQLAlchemyError as e:
            LOGGER.error("Error saving tags: %s", e)
            return existing_tags
    
    def create(self, name:str):
        """Create a new tag"""
        tag = Tag(name=name)
      
        try:
            self.session.add(tag)
            self.session.commit()
        except SQLAlchemyError as e:
            LOGGER.error("Error saving tag %s: %s", tag.name, e)
            self.session.rollback()

    def create_bulk(self, tags: list[str]) -> list[Tag]:
        """Create a list of tags"""
        if not tags:
            return []

        new_tags = self.filter_existing_tags(tags)
        if not new_tags:
            return []
        
        tag_objects = [Tag(name=tag) for tag in new_tags]

        try:
            self.session.add_all(tag_objects)
            self.session.commit()
      
            return tag_objects
        except SQLAlchemyError as e:
            LOGGER.error("Error saving tags: %s", e)
            return []

    def on_message(self, body):
        """Handle incoming messages"""
        try:
            if isinstance(body, str):
                body = json.loads(body)

            tags = body.get('tags')
            if not tags:
                LOGGER.error("No tags found in message: %s", body)
                return

            self.create_bulk(tags)
        except json.JSONDecodeError:
            LOGGER.error("Invalid JSON message: %s", body)
        except Exception as e:
            LOGGER.error("Unexpected error while processing message: %s", e)

    def filter_existing_tags(self, tags: list[str]):
        """Filter out existing tags from a list"""
        unique_tags = list(set(tags))

        if not unique_tags:
            return []
        
        existing_db_tags = self.session.query(Tag).filter(Tag.name.in_(unique_tags)).all()
        existing_tags_names = {tag.name for tag in existing_db_tags}
        
        return [tag for tag in unique_tags if tag not in existing_tags_names]