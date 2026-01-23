"""
============================================================================
Decorators Module
============================================================================
This module provides decorator functions for common patterns in test
automation, such as retry logic, execution timing, screenshot capture,
and error handling.

Key Features:
- Automatic retry on failure
- Execution time logging
- Screenshot capture on error
- Async function support
- Configurable behavior

Usage:
    from utils.decorators import async_retry, log_execution_time

    @async_retry(max_attempts=3)
    @log_execution_time
    async def flaky_operation():
        # ... operation that might fail ...
        pass

Author: Your Name
Created: 2026-01-23
============================================================================
"""

import asyncio
import functools
import time
from typing import Any, Callable, TypeVar, cast

from playwright.async_api import Page

from utils.logger import get_logger

logger = get_logger(__name__)

# Type variables for generic decorators
F = TypeVar("F", bound=Callable[..., Any])
AsyncF = TypeVar("AsyncF", bound=Callable[..., Any])


def log_execution_time(func: F) -> F:
    """
    Decorator to log the execution time of a function.

    This decorator works with both sync and async functions, measuring
    and logging their execution time for performance monitoring.

    Args:
        func: Function to decorate

    Returns:
        F: Decorated function

    Example:
        >>> @log_execution_time
        >>> async def slow_operation():
        >>>     await asyncio.sleep(2)
        >>>
        >>> await slow_operation()
        # Logs: Function 'slow_operation' took 2.00 seconds
    """

    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                elapsed = time.time() - start_time
                logger.info(f"Function '{func.__name__}' took {elapsed:.2f} seconds")

        return cast(F, async_wrapper)

    else:

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed = time.time() - start_time
                logger.info(f"Function '{func.__name__}' took {elapsed:.2f} seconds")

        return cast(F, sync_wrapper)


def async_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[AsyncF], AsyncF]:
    """
    Decorator to retry an async function on failure.

    This decorator implements exponential backoff retry logic for flaky
    operations that might fail intermittently.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each attempt (exponential backoff)
        exceptions: Tuple of exception types to catch and retry

    Returns:
        Callable[[AsyncF], AsyncF]: Decorator function

    Example:
        >>> @async_retry(max_attempts=3, delay=1.0, backoff=2.0)
        >>> async def flaky_api_call():
        >>>     response = await api.get("/data")
        >>>     return response
        >>>
        >>> # Will retry up to 3 times with delays of 1s, 2s, 4s
        >>> await flaky_api_call()
    """

    def decorator(func: AsyncF) -> AsyncF:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        logger.error(
                            f"Function '{func.__name__}' failed after {max_attempts} attempts"
                        )
                        raise

                    logger.warning(
                        f"Function '{func.__name__}' failed (attempt {attempt}/{max_attempts}). "
                        f"Retrying in {current_delay:.1f}s... Error: {e}"
                    )

                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

            # This should never be reached, but included for type safety
            if last_exception:
                raise last_exception

        return cast(AsyncF, wrapper)

    return decorator


def screenshot_on_failure(func: AsyncF) -> AsyncF:
    """
    Decorator to automatically capture a screenshot when a test fails.

    This decorator wraps async test functions and captures a screenshot
    if an exception is raised, making debugging failures easier.

    Args:
        func: Async function to decorate (must have 'page' as an argument)

    Returns:
        AsyncF: Decorated function

    Example:
        >>> @screenshot_on_failure
        >>> async def test_login(page: Page):
        >>>     await page.goto("/login")
        >>>     # If test fails here, screenshot will be captured
        >>>     await page.fill("#username", "test")
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # Try to find the 'page' argument
            page = None

            # Check positional args
            for arg in args:
                if isinstance(arg, Page):
                    page = arg
                    break

            # Check keyword args
            if page is None and "page" in kwargs:
                page = kwargs["page"]

            # Capture screenshot if we have a page
            if page:
                from utils.helpers import take_screenshot

                screenshot_path = await take_screenshot(
                    page,
                    f"{func.__name__}_failure",
                    full_page=True,
                )
                if screenshot_path:
                    logger.info(f"Failure screenshot saved: {screenshot_path}")

            # Re-raise the original exception
            raise

    return cast(AsyncF, wrapper)


def suppress_exceptions(
    exceptions: tuple[type[Exception], ...] = (Exception,),
    default_return: Any = None,
) -> Callable[[F], F]:
    """
    Decorator to suppress specified exceptions and return a default value.

    Use this decorator for operations where failure is acceptable and
    shouldn't interrupt the test flow.

    Args:
        exceptions: Tuple of exception types to suppress
        default_return: Value to return if an exception is caught

    Returns:
        Callable[[F], F]: Decorator function

    Example:
        >>> @suppress_exceptions(exceptions=(ValueError,), default_return=[])
        >>> def get_optional_data():
        >>>     # Might raise ValueError
        >>>     return process_data()
        >>>
        >>> result = get_optional_data()  # Returns [] if ValueError occurs
    """

    def decorator(func: F) -> F:
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    logger.debug(
                        f"Function '{func.__name__}' raised {type(e).__name__}: {e}. "
                        f"Returning default value: {default_return}"
                    )
                    return default_return

            return cast(F, async_wrapper)

        else:

            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logger.debug(
                        f"Function '{func.__name__}' raised {type(e).__name__}: {e}. "
                        f"Returning default value: {default_return}"
                    )
                    return default_return

            return cast(F, sync_wrapper)

    return decorator


def rate_limit(calls: int, period: float) -> Callable[[AsyncF], AsyncF]:
    """
    Decorator to rate limit function calls.

    This is useful for API calls or operations that have rate limits.

    Args:
        calls: Number of calls allowed
        period: Time period in seconds

    Returns:
        Callable[[AsyncF], AsyncF]: Decorator function

    Example:
        >>> @rate_limit(calls=10, period=60)  # Max 10 calls per minute
        >>> async def api_call():
        >>>     return await api.get("/endpoint")
    """
    min_interval = period / calls
    last_called = 0.0

    def decorator(func: AsyncF) -> AsyncF:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal last_called

            elapsed = time.time() - last_called
            if elapsed < min_interval:
                sleep_time = min_interval - elapsed
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)

            last_called = time.time()
            return await func(*args, **kwargs)

        return cast(AsyncF, wrapper)

    return decorator


def cache_result(ttl: float | None = None) -> Callable[[F], F]:
    """
    Decorator to cache function results.

    Caches the result of a function call for the specified TTL (time to live).
    Useful for expensive operations that are called multiple times with the
    same arguments.

    Args:
        ttl: Time to live in seconds (None for infinite)

    Returns:
        Callable[[F], F]: Decorator function

    Example:
        >>> @cache_result(ttl=300)  # Cache for 5 minutes
        >>> async def expensive_operation(param: str):
        >>>     # Expensive computation
        >>>     return result
    """
    cache: dict[str, tuple[Any, float]] = {}

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Create cache key from arguments
            cache_key = str((args, sorted(kwargs.items())))

            # Check cache
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if ttl is None or (time.time() - timestamp) < ttl:
                    logger.debug(f"Returning cached result for '{func.__name__}'")
                    return result

            # Call function and cache result
            result = await func(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            return result

        return cast(F, wrapper)

    return decorator


def log_function_call(func: F) -> F:
    """
    Decorator to log function calls with arguments.

    This is useful for debugging and understanding test execution flow.

    Args:
        func: Function to decorate

    Returns:
        F: Decorated function

    Example:
        >>> @log_function_call
        >>> async def login(username: str, password: str):
        >>>     # ...login logic...
        >>>
        >>> # Logs: Calling 'login' with args=('user@test.com',) kwargs={'password': '***'}
    """

    def format_args(*args: Any, **kwargs: Any) -> str:
        """Format arguments for logging, hiding sensitive data."""
        # Hide password fields
        safe_kwargs = {}
        for key, value in kwargs.items():
            if "password" in key.lower() or "secret" in key.lower():
                safe_kwargs[key] = "***"
            else:
                safe_kwargs[key] = value

        args_str = f"args={args}" if args else ""
        kwargs_str = f"kwargs={safe_kwargs}" if safe_kwargs else ""

        return f"{args_str} {kwargs_str}".strip()

    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.debug(f"Calling '{func.__name__}' with {format_args(*args, **kwargs)}")
            return await func(*args, **kwargs)

        return cast(F, async_wrapper)

    else:

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.debug(f"Calling '{func.__name__}' with {format_args(*args, **kwargs)}")
            return func(*args, **kwargs)

        return cast(F, sync_wrapper)


if __name__ == "__main__":
    """
    Module test/demonstration code.

    Run this module directly to see decorators in action:
        python -m utils.decorators
    """

    async def demo() -> None:
        print("Decorator Examples")
        print("=" * 80)

        # Example 1: Log execution time
        @log_execution_time
        async def slow_operation() -> str:
            await asyncio.sleep(1)
            return "Done"

        result = await slow_operation()
        print(f"Result: {result}\n")

        # Example 2: Retry logic
        @async_retry(max_attempts=3, delay=0.5)
        async def flaky_operation(attempt_tracker: list[int]) -> str:
            attempt_tracker.append(1)
            if len(attempt_tracker) < 3:
                raise ValueError("Not yet!")
            return "Success!"

        attempts: list[int] = []
        result = await flaky_operation(attempts)
        print(f"Result: {result}, Attempts: {len(attempts)}\n")

        # Example 3: Log function call
        @log_function_call
        async def login(username: str, password: str) -> None:
            print(f"Logging in user: {username}")

        await login("test@example.com", password="secret123")

        print("=" * 80)

    asyncio.run(demo())
