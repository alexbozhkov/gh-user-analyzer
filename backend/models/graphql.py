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
    cached: bool
    auth_used: bool
    rate_limit_limit: int | None
    rate_limit_remaining: int | None
    rate_limit_used: int | None
    rate_limit_reset: int | None
    rate_limit_resource: str | None


@strawberry.type
class Query:
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
        metadata = summary.get("metadata", {})
        rate_limit = metadata.get("rate_limit") or {}
        return UserSummaryType(
            username=summary["username"],
            followers_count=summary["followers_count"],
            repositories=repositories,
            most_used_language=summary["most_used_language"],
            technologies=summary["technologies"],
            messages=summary["messages"],
            cached=metadata.get("cached", False),
            auth_used=metadata.get("auth_used", False),
            rate_limit_limit=rate_limit.get("limit"),
            rate_limit_remaining=rate_limit.get("remaining"),
            rate_limit_used=rate_limit.get("used"),
            rate_limit_reset=rate_limit.get("reset"),
            rate_limit_resource=rate_limit.get("resource"),
        )


strawberry_schema = strawberry.Schema(query=Query)
