from fastapi import Request

from healthcheck import HealthCheckCoordinator
from healthcheck.example import ExampleHealthChecker
from models.graphql import GraphQLContext


async def get_health_check_coordinator() -> HealthCheckCoordinator:
    example_health_checker = ExampleHealthChecker()
    return HealthCheckCoordinator([example_health_checker])


async def get_graphql_context(request: Request) -> GraphQLContext:
    return GraphQLContext(github_token=request.headers.get("X-GitHub-Token"))
