from random import uniform

from config import settings
from telemetry.logger import get_logger
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from exceptions import GitHubTransportError, GitHubRestTransportError

logger = get_logger()

RETRYABLE_STATUSES = {429, 500, 502, 503, 504}


def _is_retryable(exc: Exception) -> bool:
    status = getattr(exc, "status_code", None)
    if status in RETRYABLE_STATUSES:
        return True
    if isinstance(exc, (GitHubRestTransportError, GitHubTransportError)):
        return True
    return False


def _rate_limit_aware_wait(retry_state) -> float:
    exc = retry_state.outcome.exception()
    if exc is None:
        return 0.0

    headers = getattr(exc, "headers", {}) or {}

    retry_after = headers.get("Retry-After")
    if retry_after:
        try:
            return float(retry_after) + uniform(0, 2)
        except ValueError:
            pass

    if getattr(exc, "status_code", None) == 429:
        return 60.0

    base_wait = wait_exponential(multiplier=1, min=1, max=60)(retry_state)
    return base_wait + uniform(0, 2)


def _log_retry(retry_state) -> None:
    exc = retry_state.outcome.exception()
    attempt = retry_state.attempt_number
    fn_name = repr(retry_state.fn)
    msg = exc.args[0] if exc and exc.args else "Unknown error"
    logger.warning(
        "%s failed (attempt %d/3): %s",
        fn_name,
        attempt,
        msg,
    )


def get_retry_config(attempts: int = settings.DEFAULT_RETRY_ATTEMPTS) -> AsyncRetrying:
    return AsyncRetrying(
        retry=retry_if_exception(_is_retryable),
        stop=stop_after_attempt(attempts),
        wait=_rate_limit_aware_wait,
        before_sleep=_log_retry,
        reraise=True,
    )
