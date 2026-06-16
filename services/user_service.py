"""User service — business logic for admin operations.

This is also where the stats caching logic lives: the router doesn't need to
know about Redis, it just calls service.get_stats().
"""
import json

from fastapi import Depends
from fastapi.concurrency import run_in_threadpool
from redis.asyncio import Redis

import models
from redis_client import get_redis
from repositories.user_repository import UserRepository, get_user_repository

STATS_CACHE_KEY = "stats:users"
STATS_TTL_SECONDS = 30


class UserService:
    def __init__(self, users: UserRepository, redis: Redis):
        self.users = users
        self.redis = redis

    def list_users(self) -> list[models.User]:
        return self.users.list_all()

    async def get_stats(self) -> dict:
        """Stats with caching (cache-aside). source = cache | db."""
        cached = await self.redis.get(STATS_CACHE_KEY)
        if cached is not None:
            return {"source": "cache", **json.loads(cached)}

        # repo.count is a synchronous (blocking) call; in async we offload it to a
        # thread pool so we don't stall the event loop.
        total = await run_in_threadpool(self.users.count)
        data = {"total_users": total}
        await self.redis.set(STATS_CACHE_KEY, json.dumps(data), ex=STATS_TTL_SECONDS)
        return {"source": "db", **data}


def get_user_service(
    users: UserRepository = Depends(get_user_repository),
    redis: Redis = Depends(get_redis),
) -> UserService:
    return UserService(users, redis)
