class GitHubGraphQLError(Exception): ...


class GitHubAuthenticationError(GitHubGraphQLError): ...


class GitHubTransportError(GitHubGraphQLError):
    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        headers: dict[str, str] | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.headers = headers or {}


class GitHubResponseError(GitHubGraphQLError): ...


class GitHubRestError(Exception): ...


class GitHubRestNotFoundError(GitHubRestError): ...


class GitHubRestTransportError(GitHubRestError):
    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        headers: dict[str, str] | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.headers = headers or {}


class GitHubRestResponseError(GitHubRestError):
    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        headers: dict[str, str] | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.headers = headers or {}


class UserAnalysisError(Exception): ...


class UserNotFoundError(UserAnalysisError): ...


class GraphQLRequestValidationError(Exception): ...
