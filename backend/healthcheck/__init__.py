from abc import ABC, abstractmethod
import asyncio
import os
import signal
from typing import List

from telemetry.logger import get_logger

logger = get_logger("app")


class AbstractServiceHealthChecker(ABC):
    @abstractmethod
    async def check_health(self) -> None: ...


class HealthCheckCoordinator:
    HEALTH_CHECK_TIMEOUT: int = 4  # Try to keep under the k8s health check interval
    GRACEFUL_SHUTDOWN_TIMEOUT: int = 5

    def __init__(self, service_health_checkers: List[AbstractServiceHealthChecker]):
        self.service_health_checkers = service_health_checkers

    async def run_health_checks(self):
        try:
            for checker in self.service_health_checkers:
                await asyncio.wait_for(
                    checker.check_health(), timeout=self.HEALTH_CHECK_TIMEOUT
                )
        except Exception as e:
            await self.handle_unhealthy_status(str(e))
            return False
        return True

    async def handle_unhealthy_status(self, error_message: str):
        logger.error(f"Service health check failed: {error_message}")
        logger.critical("Health check failed - initiating application shutdown")
        await self.initiate_graceful_shutdown()

    async def initiate_graceful_shutdown(self):
        logger.warning(
            f"Graceful shutdown initiated - exiting in {self.GRACEFUL_SHUTDOWN_TIMEOUT} seconds"
        )
        await asyncio.sleep(self.GRACEFUL_SHUTDOWN_TIMEOUT)
        os.kill(os.getppid(), signal.SIGTERM)
