"""
database.py
-----------
Sets up the SQLAlchemy engine, session factory, and declarative Base
that every ORM model inherits from.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session per-request and
    always closes it afterwards, even if an exception occurs."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
