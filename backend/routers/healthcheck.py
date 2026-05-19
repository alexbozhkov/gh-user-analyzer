from fastapi import APIRouter, HTTPException, Depends, status

from dependencies import get_health_check_coordinator
from healthcheck import HealthCheckCoordinator
from models import HealthCheck

healthcheck_router = APIRouter(
    prefix="",
    tags=["healthcheck"],
)


@healthcheck_router.get(
    "/healthz",
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


@healthcheck_router.get(
    "/livez",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
async def livez() -> HealthCheck:
    return HealthCheck()
