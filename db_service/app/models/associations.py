from sqlalchemy import Table, Column, Integer, ForeignKey

from app.models import Base

manga_artist = Table(
    'manga_artists', 
    Base.metadata,
    Column('manga_id', Integer, ForeignKey('mangas.id'), primary_key=True),
    Column('artist_id', Integer, ForeignKey('artists.id'), primary_key=True)
)

manga_group = Table(
    'manga_groups', 
    Base.metadata,
    Column('manga_id', Integer, ForeignKey('mangas.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups.id'), primary_key=True)
)

manga_tag = Table(
    'manga_tags', 
    Base.metadata,
    Column('manga_id', Integer, ForeignKey('mangas.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)