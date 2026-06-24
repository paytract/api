import asyncio
from functools import wraps
from collections.abc import Callable, Awaitable

import httpx
from pybreaker import (
    STATE_OPEN,
    STATE_CLOSED,
    STATE_HALF_OPEN,
    CircuitBreaker,
    CircuitBreakerState,
    CircuitBreakerListener,
)

from app.utils.logger import logger


def is_retriable_http(error: httpx.HTTPError) -> bool:
    """Determine if an HTTP error is retriable."""
    if isinstance(error, httpx.TimeoutException) or isinstance(
        error, httpx.NetworkError
    ):
        return True

    if isinstance(error, httpx.HTTPStatusError) and (
        error.response.status_code in {408, 429} or error.response.status_code >= 500
    ):
        return True

    return False


async def delay(secs: int) -> None:
    """Delay before retrying a function."""
    await asyncio.sleep(secs)


async def with_retry[T](
    operation: Callable[[], Awaitable[T]],
    max_attempts: int = 3,
    base_delay_secs: int = 1,
) -> T:
    """Execute an operation with retry logic."""
    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return await operation()
        except Exception as error:
            last_error = error

            match error:
                case e if isinstance(e, httpx.HTTPError):
                    if not is_retriable_http(e) or attempt == max_attempts:
                        raise

                    retry_after = getattr(
                        getattr(error, "response", {}), "headers", {}
                    ).get("Retry-After")
                    delay_secs = (
                        int(retry_after)
                        if retry_after and retry_after.isdigit()
                        else base_delay_secs * (2 ** (attempt - 1))
                    )

                    logger.warning(
                        f"Attempt {attempt} failed with retriable error: {error}. "
                        f"Retrying in {delay_secs} seconds..."
                    )

                    await delay(delay_secs)

                case _:
                    logger.error(
                        f"Attempt {attempt} failed with non-retriable error: {error}"
                    )
                    raise

    raise last_error if last_error else Exception("Operation failed after retries")


class BreakerListener(CircuitBreakerListener):
    """Listener for circuit breaker state changes."""

    def state_change(
        self,
        cb: CircuitBreaker,
        old_state: CircuitBreakerState | None,
        new_state: CircuitBreakerState,
    ) -> None:
        """Log circuit breaker state changes."""
        if new_state.name == STATE_OPEN:
            logger.warning("⚠️  Circuit breaker OPENED — requests will fail fast")
        elif new_state.name == STATE_HALF_OPEN:
            logger.info("🔄  Circuit breaker HALF-OPEN — testing recovery")
        elif new_state.name == STATE_CLOSED:
            logger.info("✅  Circuit breaker CLOSED — normal operation")


circuit_breaker = CircuitBreaker(
    fail_max=5, reset_timeout=30, listeners=[BreakerListener()]
)


def apply_breaker[**P, R](
    func: Callable[P, Awaitable[R]],
) -> Callable[P, Awaitable[R]]:
    """Decorator to apply circuit breaker protection to an async function."""
    protected = circuit_breaker(func)  # type: ignore

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return await protected(*args, **kwargs)  # type: ignore

    return wrapper
