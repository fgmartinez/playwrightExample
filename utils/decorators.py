"""Reusable decorators for the test framework."""

import functools
import logging
import time
from typing import Any, Callable, TypeVar, cast

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def log_execution_time(func: F) -> F:
    """Log how long a function takes to execute."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            logger.info(f"Function '{func.__name__}' took {time.time() - start:.2f}s")

    return cast(F, wrapper)
