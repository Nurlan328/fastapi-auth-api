"""Подключение к базе данных через SQLAlchemy.

Строка подключения берётся из настроек (config.settings.DATABASE_URL),
которые читаются из .env / переменных окружения.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import settings

# Аргумент check_same_thread нужен ТОЛЬКО для SQLite; для Postgres он не нужен.
connect_args = (
    {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

# Фабрика сессий — через неё мы общаемся с БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для всех ORM-моделей
Base = declarative_base()


def get_db():
    """Зависимость: открывает сессию на время запроса и закрывает её."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
