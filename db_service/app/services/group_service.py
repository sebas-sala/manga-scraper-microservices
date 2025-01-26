"""
Service class for handling groups
"""

import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import session
from app.models import Group
from app.services import Base

LOGGER = logging.getLogger(__name__)

class GroupService(Base):
    """Service class for handling artists"""

    def __init__(self, db_session: Session | None = None):
        self.session = db_session or session
        self.group_query = self.session.query(Group)

    def get_by_name(self, name: str) -> Group | None:
        """Get a tag by name"""
        return self.group_query.filter(Group.name == name).first()
    
    def get_by_names(self, names: list[str]) -> list[Group]:
        """Get tags by names"""
        return self.group_query.filter(Group.name.in_(names)).all()    
    
    def create(self, name:str):
        """Create a new tag"""
        group = Group(name=name)

        try:
            self.session.add(group)
            self.session.commit()

            return group
        except SQLAlchemyError as e:
            LOGGER.error("Error saving tag %s: %s", group.name, e)
            self.session.rollback()

    def get_or_create_many(self, names: list[str]) -> list[Group]:
        """Get or create a list of tags"""
        if not names:
            return []

        existing_groups = self.get_by_names(names)
        existing_names = {artist.name for artist in existing_groups} 

        new_groups_names = list(set(names) - existing_names)

        if not new_groups_names:
            return existing_groups

        try:
            new_groups = self.create_bulk(new_groups_names)
            return existing_groups + new_groups
        except SQLAlchemyError as e:
            LOGGER.error("Error saving tags: %s", e)
            return existing_groups

    def create_bulk(self, names: list[str]) -> list[Group]:
        """Create a list of groups"""
        if not names:
            return []

        groups_objects = [Group(name=name) for name in names]

        try:
            self.session.add_all(groups_objects)
            self.session.commit()
            return groups_objects
        except SQLAlchemyError as e:
            LOGGER.error("Error saving tags: %s", e)
            self.session.rollback()
            return []
