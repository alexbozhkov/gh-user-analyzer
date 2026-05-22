import json
from typing import Any

from redis.asyncio import Redis

from config import settings
from data_access.cache.base import CacheBackend


class RedisCacheBackend(CacheBackend):
    def __init__(self):
        self.client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def get(self, key: str) -> dict[str, Any] | None:
        value = await self.client.get(key)
        if value is None:
            return None
        return json.loads(value)

    async def set(self, key: str, value: dict[str, Any]) -> None:
        await self.client.set(key, json.dumps(value), ex=settings.CACHE_TTL)
