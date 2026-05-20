from typing import Any

from dependencies import get_graphql_context
from models.graphql import GraphQLRequest, strawberry_schema


async def execute_graphql(request, payload: GraphQLRequest) -> dict[str, Any]:
    context = await get_graphql_context(request)
    result = await strawberry_schema.execute(
        payload.query,
        variable_values=payload.variables,
        operation_name=payload.operation_name,
        context_value=context,
    )

    response: dict[str, Any] = {"data": result.data}
    if result.errors:
        response["errors"] = [{"message": error.message} for error in result.errors]
    return response
