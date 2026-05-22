from clients.github.graphql import GitHubGraphQLClient
from data_access.cache import RedisCacheBackend
from data_access.cache.keys import build_user_summary_cache_key
from data_access.repository.queries import USER_ANALYSIS_QUERY
from exceptions import UserNotFoundError


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
            return cached["data"]

        client = GitHubGraphQLClient(token=token)
        data = await client.execute(USER_ANALYSIS_QUERY, {"login": username})
        user = data.get("user")
        if user is None:
            raise UserNotFoundError(f"GitHub user '{username}' does not exist.")

        repositories = user.get("repositories", {}).get("nodes") or []
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
        }
        await self.cache.set(
            cache_key,
            {"auth_used": auth_used, "data": normalized},
        )
        return normalized
