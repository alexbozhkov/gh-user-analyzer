from healthcheck import HealthCheckCoordinator
from healthcheck.example import ExampleHealthChecker


async def get_health_check_coordinator() -> HealthCheckCoordinator:
    example_health_checker = ExampleHealthChecker()
    return HealthCheckCoordinator([example_health_checker])
