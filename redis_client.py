"""Асинхронный клиент Redis.

redis.asyncio — встроенный в пакет redis async-клиент (await-аем все операции).
decode_responses=True -> ответы приходят строками (str), а не байтами.
"""
from redis.asyncio import Redis

from config import settings

# Один общий клиент на всё приложение (внутри — пул соединений).
# Соединение ленивое: создаётся при первой реальной операции, не при импорте.
redis_client: Redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)


async def get_redis() -> Redis:
    """Зависимость FastAPI. В тестах её подменяют на fakeredis."""
    return redis_client
