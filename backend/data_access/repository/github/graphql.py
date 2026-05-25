from clients.github.graphql import GitHubGraphQLClient
from data_access.cache import RedisCacheBackend
from data_access.cache.keys import build_user_summary_cache_key
from data_access.repository.queries import USER_ANALYSIS_QUERY
from exceptions import GitHubResponseError, UserNotFoundError


class GitHubGraphQLUserRepository:
    def __init__(self, cache=None):
        self.cache = cache or RedisCacheBackend()

    async def get_user_analysis_source(
        self,
        username: str,
        token: str | None = None,
    ) -> dict:
        auth_used = bool(token)
        cache_key = build_user_summary_cache_key(
            upstream="graphql",
            username=username,
            auth_used=auth_used,
        )
        cached = await self.cache.get(cache_key)
        if cached is not None:
            cached_data = dict(cached["data"])
            metadata = dict(cached_data.get("metadata") or {})
            metadata["cached"] = True
            cached_data["metadata"] = metadata
            return cached_data

        client = GitHubGraphQLClient(token=token)
        repositories: list[dict] = []
        cursor: str | None = None
        rate_limit: dict | None = None
        user = None

        while True:
            try:
                response = await client.execute(
                    USER_ANALYSIS_QUERY,
                    {"login": username, "after": cursor},
                )
            except GitHubResponseError as exc:
                if "Could not resolve to a User" in str(exc):
                    raise UserNotFoundError(
                        f"GitHub user '{username}' does not exist."
                    ) from None
                raise

            data = response["data"]
            rate_limit = response.get("rate_limit")
            user = data.get("user")
            if user is None:
                raise UserNotFoundError(f"GitHub user '{username}' does not exist.")

            repository_connection = user.get("repositories", {})
            repositories.extend(repository_connection.get("nodes") or [])
            page_info = repository_connection.get("pageInfo") or {}
            if not page_info.get("hasNextPage"):
                break
            cursor = page_info.get("endCursor")

        normalized = {
            "username": user["login"],
            "followers_count": user.get("followers", {}).get("totalCount", 0),
            "repositories": [
                {
                    "name": repo["name"],
                    "url": repo["url"],
                    "primary_language": (repo.get("primaryLanguage") or {}).get("name"),
                    "technologies": [
                        language["name"]
                        for language in (repo.get("languages", {}).get("nodes") or [])
                        if language and language.get("name")
                    ],
                }
                for repo in repositories
            ],
            "metadata": {
                "cached": False,
                "auth_used": auth_used,
                "source": "graphql",
                "rate_limit": rate_limit,
            },
        }
        await self.cache.set(
            cache_key,
            {"auth_used": auth_used, "data": normalized},
        )
        return normalized
