"""Общие фикстуры для тестов.

Главная идея тестирования FastAPI:
1) подменяем зависимость get_db на тестовую БД (in-memory SQLite),
2) поднимаем TestClient — он шлёт запросы в приложение без реального сервера.
Так тесты быстрые, изолированные и не трогают настоящую базу.
"""
import os

# Форсим in-memory SQLite ДО импорта приложения, чтобы тесты
# не зависели от .env / Postgres и ничего не писали на диск.
os.environ["DATABASE_URL"] = "sqlite://"

import fakeredis.aioredis
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from broker import get_email_publisher
from database import Base, get_db
from main import app
from redis_client import get_redis


@pytest.fixture
def session_factory():
    """Фабрика сессий к свежей in-memory БД (новая на каждый тест)."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        # StaticPool -> одно общее соединение, чтобы in-memory БД не исчезала
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def fake_redis():
    """In-memory подделка Redis на каждый тест (без реального сервера/Docker)."""
    return fakeredis.aioredis.FakeRedis(decode_responses=True)


@pytest.fixture
def email_outbox():
    """Список «отправленных» писем — вместо реальной публикации в RabbitMQ."""
    return []


@pytest.fixture
def client(session_factory, fake_redis, email_outbox):
    """TestClient с подменёнными на тестовые зависимостями get_db, get_redis, publisher."""

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    async def override_get_redis():
        return fake_redis

    def override_get_email_publisher():
        # вместо публикации в RabbitMQ просто складываем сообщение в список
        return email_outbox.append

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    app.dependency_overrides[get_email_publisher] = override_get_email_publisher
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
