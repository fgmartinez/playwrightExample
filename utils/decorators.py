"""
Decorators
==========
Reusable decorators for the test framework.
"""

import asyncio
import functools
import logging
import time
from typing import Any, Callable, TypeVar, cast

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def log_execution_time(func: F) -> F:
    """Log how long a sync or async function takes to execute."""

    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                logger.info(f"Function '{func.__name__}' took {time.time() - start:.2f}s")

        return cast(F, async_wrapper)

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            logger.info(f"Function '{func.__name__}' took {time.time() - start:.2f}s")

    return cast(F, sync_wrapper)
