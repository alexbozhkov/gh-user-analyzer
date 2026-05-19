from fastapi import APIRouter, HTTPException

from telemetry.logger import get_logger

logger = get_logger()

users_router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@users_router.get("/data")
async def get_user_data(username: str):
    """
    TODO:
    call the GitHub API and return a dict with data or None
    """
    try:
        return {}
    except Exception as e:
        logger.error(f"Error getting data for user {username}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@users_router.get("/repos")
async def get_user_repos(username: str):
    """
    TODO:
    call the GitHub API and return a list of dicts(repos name, language/technology) with data or None
    """
    try:
        return {}
    except Exception as e:
        logger.error(f"Error getting repos for user {username}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@users_router.get("/followers")
async def get_user_followers(username: str):
    try:
        return {}
    except Exception as e:
        logger.error(f"Error getting followers for user {username}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
