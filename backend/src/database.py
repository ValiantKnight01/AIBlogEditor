"""
Database setup and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.config import settings

# Create database engine
engine = create_engine(
    settings.database.database_url,
    pool_size=settings.database.db_pool_size,
    max_overflow=settings.database.db_max_overflow,
    pool_timeout=settings.database.db_pool_timeout,
    pool_recycle=settings.database.db_pool_recycle,
    pool_pre_ping=True,  # Enable connection health checks
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Used with FastAPI Depends.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()