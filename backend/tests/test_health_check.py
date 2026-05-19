import pytest
import signal
from unittest.mock import AsyncMock, patch

from healthcheck import AbstractServiceHealthChecker, HealthCheckCoordinator


class MockHealthChecker(AbstractServiceHealthChecker):
    def __init__(self, should_fail=False, error_message="Mock health check failed"):
        self.should_fail = should_fail
        self.error_message = error_message
        self.check_called = False

    async def check_health(self) -> None:
        self.check_called = True
        if self.should_fail:
            raise Exception(self.error_message)


@pytest.mark.asyncio
async def test_run_health_checks_all_healthy():
    checker = MockHealthChecker()
    coordinator = HealthCheckCoordinator([checker])
    result = await coordinator.run_health_checks()
    assert result is True
    assert checker.check_called is True


@pytest.mark.asyncio
async def test_run_health_checks_with_failure():
    checker = MockHealthChecker(should_fail=True)
    coordinator = HealthCheckCoordinator([checker])
    coordinator.handle_unhealthy_status = AsyncMock()
    result = await coordinator.run_health_checks()
    assert result is False
    assert checker.check_called is True
    coordinator.handle_unhealthy_status.assert_called_once()


@pytest.mark.asyncio
async def test_handle_unhealthy_status():
    coordinator = HealthCheckCoordinator([])
    coordinator.initiate_graceful_shutdown = AsyncMock()
    await coordinator.handle_unhealthy_status("Test error")
    coordinator.initiate_graceful_shutdown.assert_called_once()


@pytest.mark.asyncio
async def test_initiate_graceful_shutdown():
    coordinator = HealthCheckCoordinator([])
    with (
        patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
        patch("os.kill") as mock_kill,
        patch("os.getppid", return_value=12345) as mock_getppid,
    ):
        await coordinator.initiate_graceful_shutdown()
        mock_sleep.assert_called_once_with(coordinator.GRACEFUL_SHUTDOWN_TIMEOUT)
        mock_getppid.assert_called_once()
        mock_kill.assert_called_once_with(12345, signal.SIGTERM)


@pytest.mark.asyncio
async def test_livez_success(test_client):
    response = await test_client.get("/livez")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
