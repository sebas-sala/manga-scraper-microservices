from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.models import Base, manga_tag 

class Tag(Base):
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True) 
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
          
    mangas: Mapped[list["Manga"]] = relationship("Manga", secondary=manga_tag, back_populates='tags') # type: ignore
    
    def validate_name(self, name:str):
        if not name:
            raise ValueError("Invalid tag name")
        
        if len(name) > 100:
            raise ValueError("Tag name too long")
