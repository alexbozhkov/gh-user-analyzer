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
    raise HTTPException(
        status_code=501,
        detail="REST user summary endpoint foundation is in place but not implemented yet.",
    )


@users_router.get("/repos")
async def get_user_repos(username: str):
    raise HTTPException(
        status_code=501,
        detail="REST repositories endpoint foundation is in place but not implemented yet.",
    )


@users_router.get("/followers")
async def get_user_followers(username: str):
    raise HTTPException(
        status_code=501,
        detail="REST followers endpoint foundation is in place but not implemented yet.",
    )
