from clients.github.rest import GitHubRestClient
from data_access.cache import RedisCacheBackend
from data_access.cache.keys import build_user_summary_cache_key
from exceptions import GitHubRestNotFoundError, UserNotFoundError


class GitHubRestUserRepository:
    def __init__(self, cache=None):
        self.cache = cache or RedisCacheBackend()

    async def get_user_analysis_source(
        self,
        username: str,
        token: str | None = None,
    ) -> dict:
        auth_used = bool(token)
        cache_key = build_user_summary_cache_key(
            upstream="rest",
            username=username,
            auth_used=auth_used,
        )
        cached = await self.cache.get(cache_key)
        if cached is not None:
            return cached["data"]

        client = GitHubRestClient(token=token)

        try:
            user = await client.get(f"/users/{username}")
        except GitHubRestNotFoundError as exc:
            raise UserNotFoundError(
                f"GitHub user '{username}' does not exist."
            ) from exc

        repos = await client.get(
            f"/users/{username}/repos",
            params={"per_page": 100, "type": "owner", "sort": "updated"},
        )

        repositories = []
        for repo in repos:
            languages_url = repo["languages_url"].replace(client.BASE_URL, "")
            languages_data = await client.get(languages_url)
            repositories.append(
                {
                    "name": repo["name"],
                    "url": repo["html_url"],
                    "primary_language": repo.get("language"),
                    "technologies": sorted(languages_data.keys()),
                }
            )

        normalized = {
            "username": user["login"],
            "followers_count": user.get("followers", 0),
            "repositories": repositories,
        }
        await self.cache.set(
            cache_key,
            {"auth_used": auth_used, "data": normalized},
        )
        return normalized
