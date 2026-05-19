from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI, HTTPException, Request, status

from healthcheck import HealthCheckCoordinator
from healthcheck.example import ExampleHealthChecker
from models import HealthCheck
from telemetry.logger import get_logger

logger = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Application starting up")
    yield
    logger.info("Application shutting down")
    return


app = FastAPI(title="Fastapi Template Service", version="0.1.0", lifespan=lifespan)


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


async def get_health_check_coordinator() -> HealthCheckCoordinator:
    example_health_checker = ExampleHealthChecker()
    return HealthCheckCoordinator([example_health_checker])


@app.get(
    "/healthz",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
async def health_check(
    health_check_coordinator: HealthCheckCoordinator = Depends(
        get_health_check_coordinator
    ),
) -> HealthCheck:
    try:
        if not await health_check_coordinator.run_health_checks():
            raise HTTPException(status_code=500)
        return HealthCheck()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/livez",
    tags=["healthcheck"],
    summary="Perform a Live Status Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
async def livez() -> HealthCheck:
    return HealthCheck()
