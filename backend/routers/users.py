from fastapi import APIRouter, Header, HTTPException

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
    except UserNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (UserAnalysisError, GitHubRestError) as exc:
        logger.error(f"Error getting summary for user {username}: {exc}")
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Unexpected error getting summary for user {username}: {exc}")
        raise HTTPException(status_code=500, detail="Internal server error") from exc
