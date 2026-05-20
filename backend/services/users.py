from collections import Counter

from data_access.github.repository import GitHubUserRepository


class GitHubUsers:
    def __init__(self, repository: GitHubUserRepository | None = None):
        self.repository = repository or GitHubUserRepository()

    async def get_user_summary(
        self,
        username: str,
        token: str | None = None,
    ) -> dict:
        user = await self.repository.get_user_analysis(username=username, token=token)
        repositories = user.get("repositories", {}).get("nodes") or []
        followers_count = user.get("followers", {}).get("totalCount", 0)

        technologies = self._collect_technologies(repositories)
        most_used_language = self._get_most_used_language(repositories)

        messages: list[str] = []
        if followers_count == 0:
            messages.append("This user does not have followers.")
        if not repositories:
            messages.append("This user does not have repositories.")

        return {
            "username": user["login"],
            "followers_count": followers_count,
            "repositories": [
                {
                    "name": repo["name"],
                    "url": repo["url"],
                    "primary_language": (repo.get("primaryLanguage") or {}).get("name"),
                    "technologies": self._extract_repo_languages(repo),
                }
                for repo in repositories
            ],
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
        languages = repo.get("languages", {}).get("nodes") or []
        return [
            language["name"]
            for language in languages
            if language and language.get("name")
        ]
