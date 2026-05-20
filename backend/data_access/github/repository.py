from clients.github_graphql import GitHubGraphQLClient
from data_access.github.queries import USER_ANALYSIS_QUERY
from exceptions import UserNotFoundError


class GitHubUserRepository:
    async def get_user_analysis(
        self,
        username: str,
        token: str | None = None,
    ) -> dict:
        client = GitHubGraphQLClient(token=token)
        data = await client.execute(USER_ANALYSIS_QUERY, {"login": username})
        user = data.get("user")
        if user is None:
            raise UserNotFoundError(f"GitHub user '{username}' does not exist.")
        return user
