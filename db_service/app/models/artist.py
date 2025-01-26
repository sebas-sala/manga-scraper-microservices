from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.models import Base, manga_artist

class Artist(Base):
    __tablename__ = 'artists'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)

    mangas: Mapped[list["Manga"]] = relationship(secondary=manga_artist, back_populates='artists') # type: ignore
