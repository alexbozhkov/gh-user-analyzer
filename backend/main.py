from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request

from routers.healthcheck import healthcheck_router
from routers.users import users_router
from telemetry.logger import get_logger

logger = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Application starting up")
    yield
    logger.info("Application shutting down")
    return


app = FastAPI(title="Fastapi Template Service", version="0.1.0", lifespan=lifespan)
app.include_router(healthcheck_router)
app.include_router(users_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    should_log = request.url.path not in ["/healthz", "/livez"]
    if should_log:
        logger.info(f"Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Request failed: {e}", exc_info=True)
        raise
    if should_log and response.status_code != 200:
        logger.info(
            f"Response for {request.method} {request.url}: {response.status_code}"
        )
    return response
