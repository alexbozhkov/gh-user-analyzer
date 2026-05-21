from collections import Counter

from data_access.repository.github.graphql import GitHubGraphQLUserRepository


class GitHubUsers:
    def __init__(self, repository=None):
        self.repository = repository or GitHubGraphQLUserRepository()

    async def get_user_summary(
        self,
        username: str,
        token: str | None = None,
    ) -> dict:
        source = await self.repository.get_user_analysis_source(
            username=username,
            token=token,
        )
        repositories = source.get("repositories") or []
        followers_count = source.get("followers_count", 0)

        technologies = self._collect_technologies(repositories)
        most_used_language = self._get_most_used_language(repositories)

        messages: list[str] = []
        if followers_count == 0:
            messages.append("This user does not have followers.")
        if not repositories:
            messages.append("This user does not have repositories.")

        return {
            "username": source["username"],
            "followers_count": followers_count,
            "repositories": repositories,
            "most_used_language": most_used_language,
            "technologies": technologies,
            "messages": messages,
        }

    def _get_most_used_language(self, repositories: list[dict]) -> str | None:
        languages = [
            language
            for repo in repositories
            for language in self._extract_repo_languages(repo)
        ]
        if not languages:
            return None
        return Counter(languages).most_common(1)[0][0]

    def _collect_technologies(self, repositories: list[dict]) -> list[str]:
        technologies = {
            language
            for repo in repositories
            for language in self._extract_repo_languages(repo)
        }
        return sorted(technologies)

    def _extract_repo_languages(self, repo: dict) -> list[str]:
        return repo.get("technologies") or []
