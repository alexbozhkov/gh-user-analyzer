from typing import Any

import httpx

from exceptions import (
    GitHubAuthenticationError,
    GitHubResponseError,
    GitHubTransportError,
)


class GitHubGraphQLClient:
    BASE_URL = "https://api.github.com/graphql"

    def __init__(self, token: str | None = None, timeout: float = 10.0):
        self.token = token
        self.timeout = timeout

    async def execute(
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
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.BASE_URL,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text
            raise GitHubTransportError(
                f"GitHub GraphQL request failed with status {exc.response.status_code}: {detail}"
            ) from exc
        except httpx.HTTPError as exc:
            raise GitHubTransportError("GitHub GraphQL request failed") from exc

        data = response.json()
        if data.get("errors"):
            message = "; ".join(
                error.get("message", "Unknown GitHub error") for error in data["errors"]
            )
            raise GitHubResponseError(message)

        return data.get("data", {})
