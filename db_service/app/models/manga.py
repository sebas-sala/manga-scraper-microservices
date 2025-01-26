from datetime import datetime
from sqlalchemy import Integer, String, Float, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY

from app.models import Base, manga_tag, manga_artist, manga_group

class Manga(Base):
    __tablename__ = 'mangas'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False, index=True)
    cover: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    pages: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    uploaded_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    images: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)

    tags: Mapped[list["Tag"]] = relationship("Tag", secondary=manga_tag, back_populates='mangas') # type: ignore
    artists: Mapped[list["Artist"]] = relationship(secondary=manga_artist, back_populates='mangas') # type: ignore
    groups: Mapped[list["Group"]] = relationship(secondary=manga_group, back_populates='mangas') # type: ignore