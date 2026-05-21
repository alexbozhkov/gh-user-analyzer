from clients.github.rest import GitHubRestClient
from exceptions import GitHubRestNotFoundError, UserNotFoundError


class GitHubRestUserRepository:
    async def get_user_analysis_source(
        self,
        username: str,
        token: str | None = None,
    ) -> dict:
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

        return {
            "username": user["login"],
            "followers_count": user.get("followers", 0),
            "repositories": repositories,
        }
