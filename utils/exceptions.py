"""
Custom Exceptions Module
========================
Minimal framework-specific exception. Only what provides genuine value beyond
Playwright's native errors and Python builtins is kept here.

Design Decision:
    Playwright provides detailed, contextual errors natively (TimeoutError with
    selector info, screenshot on failure, etc.). Python has built-in TimeoutError
    and ValueError. Custom exceptions are only warranted when they carry
    framework-specific structured context that native exceptions cannot.

    Previously this module had 12 custom exception classes (ConfigurationError,
    AuthenticationError, ElementNotFoundError, PageLoadError, TimeoutError,
    TestDataError, NavigationError, ValidationError, APIError, ScreenshotError,
    BrowserError). Analysis showed none were used in any test or page object.
    The custom TimeoutError shadowed Python's builtin. ValidationError shadowed
    Pydantic's. They were removed as overengineering.

Usage:
    from utils.exceptions import FrameworkError

    raise FrameworkError("Config missing", variable="BASE_URL")
"""

from typing import Any


class FrameworkError(Exception):
    """
    Base exception for framework-specific errors.

    Use this when you need to raise an error with structured context
    that isn't covered by Playwright's native exceptions or Python builtins.

    Attributes:
        message: Human-readable error description
        details: Additional context about the error
    """

    def __init__(self, message: str, **details: Any) -> None:
        self.message = message
        self.details = details
        super().__init__(self._format())

    def _format(self) -> str:
        if not self.details:
            return self.message
        detail_lines = "".join(f"\n  {k}: {v}" for k, v in self.details.items())
        return f"{self.message}{detail_lines}"
