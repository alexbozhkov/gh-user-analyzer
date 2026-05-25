from typing import Any

import httpx

from clients.github.retry import get_retry_config
from config import settings
from exceptions import (
    GitHubRestNotFoundError,
    GitHubRestResponseError,
    GitHubRestTransportError,
)


class GitHubRestClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str | None = None):
        self.token = token

    def _build_headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github+json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        attempts: int = settings.DEFAULT_RETRY_ATTEMPTS,
    ) -> Any:
        retry_config = get_retry_config(attempts=attempts)
        async for attempt in retry_config:
            with attempt:
                return await self._get(path, params=params)

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        try:
            async with httpx.AsyncClient(
                base_url=self.BASE_URL,
                timeout=httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=10.0),
                headers=self._build_headers(),
            ) as client:
                response = await client.get(path, params=params)
        except httpx.TimeoutException as exc:
            raise GitHubRestTransportError(
                "GitHub REST request timed out",
                status_code=None,
                headers=None,
            ) from exc
        except httpx.HTTPError as exc:
            raise GitHubRestTransportError(
                "GitHub REST request failed",
                status_code=None,
                headers=None,
            ) from exc

        if response.status_code == 404:
            raise GitHubRestNotFoundError("GitHub resource was not found")
        if response.status_code >= 400:
            raise GitHubRestResponseError(
                f"GitHub REST request failed with status {response.status_code}: {response.text}",
                status_code=response.status_code,
                headers=dict(response.headers),
            )

        return {
            "data": response.json(),
            "rate_limit": {
                "limit": _to_int(response.headers.get("x-ratelimit-limit")),
                "remaining": _to_int(response.headers.get("x-ratelimit-remaining")),
                "used": _to_int(response.headers.get("x-ratelimit-used")),
                "reset": _to_int(response.headers.get("x-ratelimit-reset")),
                "resource": response.headers.get("x-ratelimit-resource"),
            },
        }


def _to_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None
