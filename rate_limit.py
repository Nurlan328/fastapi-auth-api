"""Rate limiting via Redis.

Why: protection against password brute-forcing and API abuse.
This is the "API Security" requirement.

How it works (fixed-window algorithm):
  - on each request, increment a counter in Redis keyed by IP+path (INCR);
  - on the first request, set the key's TTL (EXPIRE) = window in seconds;
  - if the counter exceeds the limit, respond 429 Too Many Requests.
The counter disappears on its own when the window expires.
"""
from fastapi import Depends, HTTPException, Request, status
from redis.asyncio import Redis

from redis_client import get_redis


class RateLimiter:
    """Dependency factory: RateLimiter(times=5, seconds=60) -> at most 5 requests per minute."""

    def __init__(self, times: int, seconds: int):
        self.times = times
        self.seconds = seconds

    async def __call__(self, request: Request, redis: Redis = Depends(get_redis)) -> None:
        ident = request.client.host if request.client else "unknown"
        key = f"ratelimit:{request.url.path}:{ident}"

        current = await redis.incr(key)
        if current == 1:
            # first request in the window — start the key's timer
            await redis.expire(key, self.seconds)

        if current > self.times:
            ttl = await redis.ttl(key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many requests. Try again in {ttl} seconds.",
                headers={"Retry-After": str(ttl)},
            )
