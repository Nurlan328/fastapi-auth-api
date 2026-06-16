"""Async Redis client.

redis.asyncio is the async client bundled with the redis package (await all ops).
decode_responses=True -> responses come back as str, not bytes.
"""
from redis.asyncio import Redis

from config import settings

# A single client for the whole app (a connection pool lives inside).
# The connection is lazy: created on the first real operation, not on import.
redis_client: Redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)


async def get_redis() -> Redis:
    """FastAPI dependency. Overridden with fakeredis in tests."""
    return redis_client
