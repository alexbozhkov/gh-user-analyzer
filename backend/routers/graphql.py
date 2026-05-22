from fastapi import APIRouter, Request

from exceptions import GraphQLRequestValidationError
from models.graphql import GraphQLRequest
from services.graphql import execute_graphql as execute_graphql_request

graphql_router = APIRouter(prefix="/graphql", tags=["graphql"])


@graphql_router.post("")
async def execute_graphql(request: Request, payload: GraphQLRequest):
    try:
        return await execute_graphql_request(request, payload)
    except GraphQLRequestValidationError as exc:
        return {"data": None, "errors": [{"message": str(exc)}]}
