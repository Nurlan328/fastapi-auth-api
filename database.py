"""Database connection via SQLAlchemy.

The connection string comes from settings (config.settings.DATABASE_URL),
which are read from .env / environment variables.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import settings

# check_same_thread is needed ONLY for SQLite; Postgres does not need it.
connect_args = (
    {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

# Session factory — we talk to the DB through it.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models.
Base = declarative_base()


def get_db():
    """Dependency: opens a session for the request and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
