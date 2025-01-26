from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import Config

engine = create_engine(Config.DATABASE_URL)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
