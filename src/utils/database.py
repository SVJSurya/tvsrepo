from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.models import Base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./emi_voicebot.db")

# For demo purposes, we'll use SQLite
if "postgresql" in DATABASE_URL:
    # Use PostgreSQL settings
    engine = create_engine(DATABASE_URL)
else:
    # Use SQLite for demo
    engine = create_engine(
        "sqlite:///./emi_voicebot.db", connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_database():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def get_db_session() -> Session:
    """Get a database session"""
    return SessionLocal()
