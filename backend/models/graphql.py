from typing import Any

from graphql import GraphQLError
from pydantic import BaseModel, Field
import strawberry
from strawberry.fastapi import BaseContext
from strawberry.types import Info

from data_access.repository.github.graphql import GitHubGraphQLUserRepository
from exceptions import GitHubGraphQLError, UserAnalysisError
from services.users import GitHubUsers


class GraphQLContext(BaseContext):
    def __init__(self, github_token: str | None = None):
        self.github_token = github_token
        self.user_service = GitHubUsers(repository=GitHubGraphQLUserRepository())


class GraphQLRequest(BaseModel):
    query: str = Field(..., min_length=1)
    variables: dict[str, Any] | None = None
    operation_name: str | None = Field(default=None, alias="operationName")


@strawberry.type
class RepositoryType:
    name: str
    url: str
    primary_language: str | None
    technologies: list[str]


@strawberry.type
class UserSummaryType:
    username: str
    followers_count: int
    repositories: list[RepositoryType]
    most_used_language: str | None
    technologies: list[str]
    messages: list[str]


@strawberry.type
class Query:
    @strawberry.field
    def health(self) -> str:
        return "ok"

    @strawberry.field
    async def user_summary(
        self,
        info: Info[GraphQLContext, None],
        username: str,
    ) -> UserSummaryType:
        try:
            summary = await info.context.user_service.get_user_summary(
                username=username,
                token=info.context.github_token,
            )
        except (GitHubGraphQLError, UserAnalysisError) as exc:
            raise GraphQLError(str(exc)) from exc

        repositories = [RepositoryType(**repo) for repo in summary["repositories"]]
        return UserSummaryType(
            username=summary["username"],
            followers_count=summary["followers_count"],
            repositories=repositories,
            most_used_language=summary["most_used_language"],
            technologies=summary["technologies"],
            messages=summary["messages"],
        )


strawberry_schema = strawberry.Schema(query=Query)
