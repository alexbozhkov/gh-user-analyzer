from abc import ABC, abstractmethod
from typing import Any


class CacheBackend(ABC):
    @abstractmethod
    async def get(self, key: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    async def set(self, key: str, value: dict[str, Any]) -> None:
        raise NotImplementedError
