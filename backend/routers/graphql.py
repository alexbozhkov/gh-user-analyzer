from fastapi import APIRouter, HTTPException, Request

from exceptions import GraphQLRequestValidationError
from models.graphql import GraphQLRequest
from services.graphql import execute_graphql as execute_graphql_request

graphql_router = APIRouter(prefix="/graphql", tags=["graphql"])

ERROR_STATUS_MAP: dict[str, int] = {
    "GitHubAuthenticationError": 400,
    "GitHubTransportError": 502,
    "GitHubResponseError": 502,
    "UserAnalysisError": 502,
    "UserNotFoundError": 404,
}


@graphql_router.post("")
async def execute_graphql(request: Request, payload: GraphQLRequest):
    try:
        result = await execute_graphql_request(request, payload)
    except GraphQLRequestValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if result.get("errors"):
        error = result["errors"][0]
        message = error["message"]
        extensions = error.get("extensions", {})
        error_type = extensions.get("type", "")
        status_code = ERROR_STATUS_MAP.get(error_type, 502)

        if "Bad credentials" in message or "401" in message:
            status_code = 401

        raise HTTPException(status_code=status_code, detail=message)

    return result
