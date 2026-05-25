from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse

from data_access.repository.github.rest import GitHubRestUserRepository
from exceptions import GitHubRestError, UserAnalysisError, UserNotFoundError
from services.users import GitHubUsers
from telemetry.logger import get_logger

logger = get_logger()
users_service = GitHubUsers(repository=GitHubRestUserRepository())

users_router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@users_router.get("")
async def get_user_summary(
    username: str,
    x_github_token: str | None = Header(default=None),
):
    try:
        return await users_service.get_user_summary(username, token=x_github_token)
    except UserNotFoundError:
        logger.warning("User '%s' not found", username)
        return JSONResponse(
            status_code=404,
            content={"detail": f"GitHub user '{username}' does not exist."},
        )
    except (UserAnalysisError, GitHubRestError) as exc:
        logger.error("Error getting summary for user '%s': %s", username, exc)
        return JSONResponse(status_code=502, content={"detail": str(exc)})
    except Exception:
        logger.exception("Unexpected error getting summary for user '%s'", username)
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )
