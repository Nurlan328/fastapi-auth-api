"""Shared fixtures for tests.

The core idea of testing FastAPI:
1) override the get_db dependency with a test DB (in-memory SQLite),
2) spin up a TestClient — it sends requests to the app without a real server.
This makes tests fast, isolated, and untouched by the real database.
"""
import os

# Force in-memory SQLite BEFORE importing the app, so tests don't depend on
# .env / Postgres and write nothing to disk.
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
    """A session factory for a fresh in-memory DB (new per test)."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        # StaticPool -> one shared connection so the in-memory DB doesn't vanish
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def fake_redis():
    """An in-memory Redis fake per test (no real server/Docker)."""
    return fakeredis.aioredis.FakeRedis(decode_responses=True)


@pytest.fixture
def email_outbox():
    """A list of "sent" emails — instead of real publishing to RabbitMQ."""
    return []


@pytest.fixture
def client(session_factory, fake_redis, email_outbox):
    """TestClient with get_db, get_redis, and the publisher overridden for tests."""

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    async def override_get_redis():
        return fake_redis

    def override_get_email_publisher():
        # instead of publishing to RabbitMQ, just append the message to a list
        return email_outbox.append

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    app.dependency_overrides[get_email_publisher] = override_get_email_publisher
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
