"""
Utils Module
============
Utility functions, helpers, exceptions, and decorators for the test framework.

Usage:
    from utils import get_logger, FrameworkError
    from utils.helpers import take_screenshot, wait_for_condition
"""

from utils.decorators import async_retry, log_execution_time, screenshot_on_failure
from utils.exceptions import FrameworkError
from utils.helpers import (
    generate_random_email,
    generate_random_string,
    get_timestamp,
    sanitize_filename,
    take_screenshot,
)
from utils.logger import get_logger, setup_logger

__all__ = [
    # Logger
    "get_logger",
    "setup_logger",
    # Exceptions
    "FrameworkError",
    # Helpers
    "take_screenshot",
    "get_timestamp",
    "sanitize_filename",
    "generate_random_string",
    "generate_random_email",
    # Decorators
    "async_retry",
    "log_execution_time",
    "screenshot_on_failure",
]
