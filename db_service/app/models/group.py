from sqlalchemy import String
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.models import Base, manga_group

class Group(Base):
    __tablename__ = 'groups'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True) 

    mangas: Mapped[list["Manga"]] = relationship(secondary=manga_group, back_populates='groups') # type: ignore