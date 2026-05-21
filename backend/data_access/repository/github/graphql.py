from clients.github.graphql import GitHubGraphQLClient
from data_access.repository.queries import USER_ANALYSIS_QUERY
from exceptions import UserNotFoundError


class GitHubGraphQLUserRepository:
    async def get_user_analysis_source(
        self,
        username: str,
        token: str | None = None,
    ) -> dict:
        client = GitHubGraphQLClient(token=token)
        data = await client.execute(USER_ANALYSIS_QUERY, {"login": username})
        user = data.get("user")
        if user is None:
            raise UserNotFoundError(f"GitHub user '{username}' does not exist.")

        repositories = user.get("repositories", {}).get("nodes") or []
        return {
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
