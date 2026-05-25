from typing import Any

import httpx

from clients.github.retry import get_retry_config
from exceptions import (
    GitHubAuthenticationError,
    GitHubResponseError,
    GitHubTransportError,
)


class GitHubGraphQLClient:
    BASE_URL = "https://api.github.com/graphql"

    def __init__(self, token: str | None = None):
        self.token = token

    async def execute(
        self, query: str, variables: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        retry_config = get_retry_config()
        async for attempt in retry_config:
            with attempt:
                return await self._do_execute(query, variables=variables)

    async def _do_execute(
        self, query: str, variables: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        if not self.token:
            raise GitHubAuthenticationError(
                "GitHub GraphQL requires a token. Provide X-GitHub-Token or set GITHUB_TOKEN."
            )

        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
        }
        payload = {"query": query, "variables": variables or {}}

        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=10.0),
            ) as client:
                response = await client.post(
                    self.BASE_URL,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise GitHubTransportError(
                "GitHub GraphQL request timed out",
                status_code=None,
                headers=None,
            ) from exc
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text
            raise GitHubTransportError(
                f"GitHub GraphQL request failed with status {exc.response.status_code}: {detail}",
                status_code=exc.response.status_code,
                headers=dict(exc.response.headers),
            ) from exc
        except httpx.HTTPError as exc:
            raise GitHubTransportError(
                "GitHub GraphQL request failed",
                status_code=None,
                headers=None,
            ) from exc

        data = response.json()
        if data.get("errors"):
            message = "; ".join(
                error.get("message", "Unknown GitHub error") for error in data["errors"]
            )
            raise GitHubResponseError(message)

        return {
            "data": data.get("data", {}),
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
