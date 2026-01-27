"""
============================================================================
Custom Exceptions Module
============================================================================
This module defines custom exception classes for the test framework,
providing more specific and meaningful error handling than generic Python
exceptions.

Benefits of Custom Exceptions:
- More descriptive error messages
- Better error categorization
- Easier debugging and troubleshooting
- Cleaner exception handling code
- Framework-specific context

Exception Hierarchy:
    TestException (base)
    ├── ConfigurationError
    ├── AuthenticationError
    ├── ElementNotFoundError
    ├── PageLoadError
    ├── TimeoutError
    └── TestDataError

Usage:
    from utils.exceptions import ElementNotFoundError, TimeoutError

    if not element:
        raise ElementNotFoundError("Submit button not found", selector="button[type='submit']")

Author: Your Name
Created: 2026-01-23
============================================================================
"""

from typing import Any


class TestException(Exception):
    """
    Base exception class for all framework-specific exceptions.

    This is the root of the custom exception hierarchy. All framework
    exceptions should inherit from this class to allow catching all
    framework-specific errors with a single except clause.

    Attributes:
        message: Human-readable error description
        details: Additional context about the error
    """

    def __init__(self, message: str, **details: Any) -> None:
        """
        Initialize the exception.

        Args:
            message: Human-readable error description
            **details: Additional context as keyword arguments
        """
        self.message = message
        self.details = details
        super().__init__(self.format_message())

    def format_message(self) -> str:
        """
        Format the exception message with details.

        Returns:
            str: Formatted error message

        Example:
            >>> exc = TestException("Error occurred", user="john", code=404)
            >>> print(exc.format_message())
            Error occurred
            Details:
              user: john
              code: 404
        """
        if not self.details:
            return self.message

        details_str = "\nDetails:\n"
        for key, value in self.details.items():
            details_str += f"  {key}: {value}\n"

        return self.message + details_str


class ConfigurationError(TestException):
    """
    Raised when there's an error in configuration.

    This exception is raised when:
    - Required configuration is missing
    - Configuration values are invalid
    - Configuration files cannot be loaded
    - Environment variables are not set

    Example:
        >>> if not base_url:
        >>>     raise ConfigurationError(
        >>>         "Base URL not configured",
        >>>         env="production",
        >>>         config_file=".env"
        >>>     )
    """

    pass


class AuthenticationError(TestException):
    """
    Raised when authentication or authorization fails.

    This exception is raised when:
    - Login fails
    - Credentials are invalid
    - Session expires
    - User lacks required permissions

    Example:
        >>> if not login_successful:
        >>>     raise AuthenticationError(
        >>>         "Login failed",
        >>>         username=username,
        >>>         reason="Invalid credentials"
        >>>     )
    """

    pass


class ElementNotFoundError(TestException):
    """
    Raised when a page element cannot be found.

    This exception is raised when:
    - Element matching selector doesn't exist
    - Element is not in the DOM
    - Selector is incorrect
    - Page structure has changed

    Example:
        >>> if not element:
        >>>     raise ElementNotFoundError(
        >>>         "Login button not found",
        >>>         selector="button#login",
        >>>         page=page.url
        >>>     )
    """

    pass


class PageLoadError(TestException):
    """
    Raised when a page fails to load properly.

    This exception is raised when:
    - Page returns error status code
    - Page load times out
    - Required page elements are missing
    - Page is in an unexpected state

    Example:
        >>> if response.status != 200:
        >>>     raise PageLoadError(
        >>>         "Page failed to load",
        >>>         url=page.url,
        >>>         status_code=response.status
        >>>     )
    """

    pass


class TimeoutError(TestException):
    """
    Raised when an operation exceeds the timeout limit.

    This exception is raised when:
    - Element doesn't appear within timeout
    - Page load exceeds timeout
    - API call times out
    - Condition is not met within timeout

    Example:
        >>> raise TimeoutError(
        >>>     "Element did not become visible",
        >>>     selector="div.content",
        >>>     timeout=30000,
        >>>     state="visible"
        >>>     )
    """

    pass


class TestDataError(TestException):
    """
    Raised when there's an issue with test data.

    This exception is raised when:
    - Test data file is missing
    - Test data is invalid
    - Data generation fails
    - Required test data is not available

    Example:
        >>> if not test_users:
        >>>     raise TestDataError(
        >>>         "No test users available",
        >>>         data_file="users.json",
        >>>         required_count=5
        >>>     )
    """

    pass


class NavigationError(TestException):
    """
    Raised when page navigation fails.

    This exception is raised when:
    - Navigation to URL fails
    - Redirect fails
    - Back/forward navigation fails
    - Page is not accessible

    Example:
        >>> raise NavigationError(
        >>>     "Failed to navigate to page",
        >>>     target_url=url,
        >>>     current_url=page.url
        >>>     )
    """

    pass


class ValidationError(TestException):
    r"""
    Raised when data validation fails.

    This exception is raised when:
    - Form validation fails
    - API response doesn't match schema
    - Test assertions fail
    - Data doesn't meet expected format

    Example:
        >>> if not is_valid_email(email):
        >>>     raise ValidationError(
        >>>         "Invalid email format",
        >>>         email=email,
        >>>         expected_pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$"
        >>>     )
    """

    pass


class APIError(TestException):
    """
    Raised when API request fails.

    This exception is raised when:
    - API returns error status code
    - API response is invalid
    - API endpoint is not available
    - API authentication fails

    Example:
        >>> if response.status >= 400:
        >>>     raise APIError(
        >>>         "API request failed",
        >>>         endpoint="/api/users",
        >>>         status_code=response.status,
        >>>         response_body=await response.text()
        >>>     )
    """

    pass


class ScreenshotError(TestException):
    """
    Raised when screenshot capture fails.

    This exception is raised when:
    - Screenshot cannot be saved
    - Screenshot directory is not writable
    - Browser doesn't support screenshots

    Example:
        >>> raise ScreenshotError(
        >>>     "Failed to capture screenshot",
        >>>     path=screenshot_path,
        >>>     reason="Directory not writable"
        >>>     )
    """

    pass


class BrowserError(TestException):
    """
    Raised when browser operation fails.

    This exception is raised when:
    - Browser fails to launch
    - Browser crashes
    - Browser context creation fails
    - Browser doesn't support feature

    Example:
        >>> raise BrowserError(
        >>>     "Failed to launch browser",
        >>>     browser_type="chromium",
        >>>     error=str(e)
        >>>     )
    """

    pass


if __name__ == "__main__":
    """
    Module test/demonstration code.

    Run this module directly to see exception formatting:
        python -m utils.exceptions
    """
    print("Custom Exception Examples")
    print("=" * 80)

    # Example 1: Basic exception
    try:
        raise TestException("Something went wrong")
    except TestException as e:
        print(f"1. {e}\n")

    # Example 2: Exception with details
    try:
        raise ElementNotFoundError(
            "Login button not found",
            selector="button#login",
            page="/login",
            timeout=5000,
        )
    except ElementNotFoundError as e:
        print(f"2. {e}\n")

    # Example 3: Configuration error
    try:
        raise ConfigurationError(
            "Missing required environment variable",
            variable="BASE_URL",
            environment="production",
        )
    except ConfigurationError as e:
        print(f"3. {e}\n")

    # Example 4: Catching base exception
    try:
        raise APIError(
            "API request failed",
            endpoint="/api/users",
            status_code=404,
        )
    except TestException as e:  # Catches all framework exceptions
        print(f"4. Caught using base class: {e}\n")

    print("=" * 80)
