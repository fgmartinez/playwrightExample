"""
============================================================================
Utils Module
============================================================================
This module provides utility functions, helpers, custom exceptions, and
decorators used throughout the test framework.

Key Components:
- Logger: Centralized logging configuration
- Helpers: Common utility functions
- Exceptions: Custom exception classes
- Decorators: Function decorators for retry, timing, etc.

Usage:
    from utils import get_logger, retry, TestException
    from utils.helpers import take_screenshot, wait_for_condition

Author: Your Name
Created: 2026-01-23
============================================================================
"""

from utils.decorators import async_retry, log_execution_time, screenshot_on_failure
from utils.exceptions import (
    AuthenticationError,
    ConfigurationError,
    ElementNotFoundError,
    PageLoadError,
    TestDataError,
    TestException,
    TimeoutError,
)
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
    "TestException",
    "ConfigurationError",
    "AuthenticationError",
    "ElementNotFoundError",
    "PageLoadError",
    "TimeoutError",
    "TestDataError",
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
