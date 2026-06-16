"""Rate limiting (ограничение частоты запросов) через Redis.

Зачем: защита от перебора паролей (брутфорса) и злоупотреблений API.
Это пункт «API Security» из требований.

Как работает (алгоритм "fixed window"):
  - на каждый запрос увеличиваем счётчик в Redis по ключу IP+путь (INCR);
  - при первом запросе ставим ключу время жизни (EXPIRE) = окно в секундах;
  - если счётчик превысил лимит — отвечаем 429 Too Many Requests.
Счётчик сам исчезает по истечении окна.
"""
from fastapi import Depends, HTTPException, Request, status
from redis.asyncio import Redis

from redis_client import get_redis


class RateLimiter:
    """Зависимость-фабрика: RateLimiter(times=5, seconds=60) -> не больше 5 запросов в минуту."""

    def __init__(self, times: int, seconds: int):
        self.times = times
        self.seconds = seconds

    async def __call__(self, request: Request, redis: Redis = Depends(get_redis)) -> None:
        ident = request.client.host if request.client else "unknown"
        key = f"ratelimit:{request.url.path}:{ident}"

        current = await redis.incr(key)
        if current == 1:
            # это первый запрос в окне — заводим таймер на ключ
            await redis.expire(key, self.seconds)

        if current > self.times:
            ttl = await redis.ttl(key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Слишком много запросов. Попробуй через {ttl} сек.",
                headers={"Retry-After": str(ttl)},
            )