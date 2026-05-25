from typing import Any

from graphql import OperationType, parse
from dependencies import get_graphql_context
from exceptions import GraphQLRequestValidationError
from models.graphql import GraphQLRequest, strawberry_schema

ALLOWED_ROOT_FIELDS = {"userSummary"}


def validate_graphql_request(query: str) -> None:
    document = parse(query)
    operations = [
        definition
        for definition in document.definitions
        if getattr(definition, "operation", None) is not None
    ]

    if len(operations) != 1:
        raise GraphQLRequestValidationError(
            "Only a single GraphQL operation is allowed."
        )

    operation = operations[0]
    if operation.operation != OperationType.QUERY:
        raise GraphQLRequestValidationError(
            "Only GraphQL query operations are allowed."
        )

    for selection in operation.selection_set.selections:
        field_name = getattr(getattr(selection, "name", None), "value", None)
        if field_name not in ALLOWED_ROOT_FIELDS:
            raise GraphQLRequestValidationError(
                "Only the userSummary query is allowed."
            )


async def execute_graphql(request, payload: GraphQLRequest) -> dict[str, Any]:
    validate_graphql_request(payload.query)

    context = await get_graphql_context(request)
    if not context.github_token:
        raise GraphQLRequestValidationError(
            "X-GitHub-Token is required for the GraphQL endpoint."
        )

    result = await strawberry_schema.execute(
        payload.query,
        variable_values=payload.variables,
        operation_name=payload.operation_name,
        context_value=context,
    )

    response: dict[str, Any] = {"data": result.data}
    if result.errors:
        response["errors"] = [
            {"message": error.message, "extensions": error.extensions or {}}
            for error in result.errors
        ]
    return response
