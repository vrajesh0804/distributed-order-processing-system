"""
Database setup using SQLAlchemy.

Packages used:
- create_engine: creates connection engine for PostgreSQL.
- sessionmaker: creates database sessions for each API request.
- declarative_base: base class used by SQLAlchemy models.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides one DB session per request.

    It opens a session before the route runs and closes it after the route ends.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
