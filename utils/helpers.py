"""
============================================================================
Helper Utilities Module
============================================================================
This module provides utility functions used throughout the test framework
for common operations like screenshot capture, string manipulation, data
generation, and file operations.

Key Features:
- Screenshot management
- String utilities
- Random data generation
- File system operations
- Date/time utilities
- Async helpers

Usage:
    from utils.helpers import take_screenshot, generate_random_email

    # Take screenshot
    await take_screenshot(page, "login_page")

    # Generate test data
    email = generate_random_email()

Author: Your Name
Created: 2026-01-23
============================================================================
"""

import asyncio
import random
import re
import string
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, TypeVar

from faker import Faker
from playwright.async_api import Page

from config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Faker for generating realistic test data
faker = Faker()

# Type variable for generic functions
T = TypeVar("T")


async def take_screenshot(
    page: Page,
    name: str,
    full_page: bool = False,
) -> Path | None:
    """
    Capture a screenshot of the current page.

    This function saves a screenshot with a timestamped filename to help
    with debugging test failures and documenting test execution.

    Args:
        page: Playwright page instance
        name: Base name for the screenshot file (without extension)
        full_page: Whether to capture the full scrollable page

    Returns:
        Path | None: Path to the saved screenshot, or None if capture fails

    Example:
        >>> screenshot_path = await take_screenshot(page, "login_error")
        >>> assert screenshot_path.exists()
    """
    try:
        # Create screenshots directory
        screenshots_dir = settings.project_root / "reports" / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp
        timestamp = get_timestamp()
        filename = sanitize_filename(f"{name}_{timestamp}.png")
        screenshot_path = screenshots_dir / filename

        # Capture screenshot
        await page.screenshot(
            path=str(screenshot_path),
            full_page=full_page,
        )

        logger.info(f"Screenshot saved: {screenshot_path}")
        return screenshot_path

    except Exception as e:
        logger.error(f"Failed to capture screenshot: {e}")
        return None


def get_timestamp(format_string: str = "%Y%m%d_%H%M%S") -> str:
    """
    Get current timestamp as formatted string.

    Args:
        format_string: strftime format string

    Returns:
        str: Formatted timestamp

    Example:
        >>> timestamp = get_timestamp()
        >>> print(timestamp)
        '20260123_143052'
    """
    return datetime.now().strftime(format_string)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string to be used as a filename.

    This function removes or replaces characters that are invalid or
    problematic in filenames across different operating systems.

    Args:
        filename: Original filename string

    Returns:
        str: Sanitized filename

    Example:
        >>> sanitize_filename("test: results #1.txt")
        'test_results_1.txt'
    """
    # Replace invalid characters with underscore
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)

    # Replace multiple underscores with single underscore
    filename = re.sub(r"_+", "_", filename)

    # Remove leading/trailing underscores and whitespace
    filename = filename.strip("_ ")

    return filename


def generate_random_string(length: int = 10, include_digits: bool = True) -> str:
    """
    Generate a random string of specified length.

    Args:
        length: Length of the string to generate
        include_digits: Whether to include digits in the string

    Returns:
        str: Random string

    Example:
        >>> random_str = generate_random_string(8, include_digits=True)
        >>> len(random_str)
        8
    """
    characters = string.ascii_letters
    if include_digits:
        characters += string.digits

    return "".join(random.choice(characters) for _ in range(length))


def generate_random_email(domain: str = "test.com") -> str:
    """
    Generate a random email address.

    Args:
        domain: Email domain

    Returns:
        str: Random email address

    Example:
        >>> email = generate_random_email()
        >>> assert "@" in email
        >>> assert email.endswith("test.com")
    """
    username = generate_random_string(10).lower()
    return f"{username}@{domain}"


def generate_random_phone() -> str:
    """
    Generate a random phone number in US format.

    Returns:
        str: Random phone number (format: XXX-XXX-XXXX)

    Example:
        >>> phone = generate_random_phone()
        >>> assert len(phone) == 12  # including dashes
    """
    return f"{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"


def generate_random_zipcode() -> str:
    """
    Generate a random US ZIP code.

    Returns:
        str: Random 5-digit ZIP code

    Example:
        >>> zipcode = generate_random_zipcode()
        >>> assert len(zipcode) == 5
        >>> assert zipcode.isdigit()
    """
    return f"{random.randint(10000, 99999)}"


def generate_test_user_data() -> dict[str, str]:
    """
    Generate a complete set of test user data.

    Returns:
        dict[str, str]: Dictionary with user information

    Example:
        >>> user_data = generate_test_user_data()
        >>> assert "firstName" in user_data
        >>> assert "email" in user_data
    """
    return {
        "firstName": faker.first_name(),
        "lastName": faker.last_name(),
        "email": faker.email(),
        "phone": generate_random_phone(),
        "address": faker.street_address(),
        "city": faker.city(),
        "state": faker.state_abbr(),
        "zipCode": generate_random_zipcode(),
        "company": faker.company(),
    }


async def wait_for_condition(
    condition: Callable[[], bool | Any],
    timeout: int = 30000,
    poll_interval: int = 500,
    error_message: str = "Condition not met within timeout",
) -> bool:
    """
    Wait for a condition to become true.

    This is a generic utility for waiting on custom conditions that aren't
    directly supported by Playwright's wait functions.

    Args:
        condition: Callable that returns True when condition is met
        timeout: Maximum time to wait in milliseconds
        poll_interval: Time between condition checks in milliseconds
        error_message: Error message if timeout is reached

    Returns:
        bool: True if condition was met

    Raises:
        TimeoutError: If condition is not met within timeout

    Example:
        >>> async def is_data_loaded():
        >>>     return len(await page.query_selector_all(".item")) > 0
        >>>
        >>> await wait_for_condition(is_data_loaded, timeout=10000)
    """
    start_time = asyncio.get_event_loop().time()
    timeout_seconds = timeout / 1000
    poll_seconds = poll_interval / 1000

    while True:
        try:
            if condition():
                return True
        except Exception as e:
            logger.debug(f"Condition check raised exception: {e}")

        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed >= timeout_seconds:
            raise TimeoutError(error_message)

        await asyncio.sleep(poll_seconds)


def format_currency(amount: float) -> str:
    """
    Format a number as USD currency.

    Args:
        amount: Numeric amount

    Returns:
        str: Formatted currency string

    Example:
        >>> format_currency(29.99)
        '$29.99'
        >>> format_currency(1234.5)
        '$1,234.50'
    """
    return f"${amount:,.2f}"


def parse_currency(currency_string: str) -> float:
    """
    Parse a currency string to a float.

    Args:
        currency_string: Currency string (e.g., "$29.99")

    Returns:
        float: Numeric value

    Example:
        >>> parse_currency("$29.99")
        29.99
        >>> parse_currency("$1,234.50")
        1234.5
    """
    # Remove currency symbol, commas, and whitespace
    cleaned = re.sub(r"[$,\s]", "", currency_string)
    return float(cleaned)


async def scroll_to_element(page: Page, selector: str) -> None:
    """
    Scroll to make an element visible in the viewport.

    Args:
        page: Playwright page instance
        selector: CSS selector for the element

    Example:
        >>> await scroll_to_element(page, "footer")
    """
    await page.locator(selector).scroll_into_view_if_needed()
    logger.debug(f"Scrolled to element: {selector}")


async def get_element_text(page: Page, selector: str) -> str:
    """
    Get the text content of an element.

    Args:
        page: Playwright page instance
        selector: CSS selector for the element

    Returns:
        str: Text content of the element

    Example:
        >>> text = await get_element_text(page, "h1")
        >>> print(text)
    """
    element = page.locator(selector)
    text = await element.text_content()
    return text.strip() if text else ""


async def get_elements_count(page: Page, selector: str) -> int:
    """
    Get the count of elements matching a selector.

    Args:
        page: Playwright page instance
        selector: CSS selector

    Returns:
        int: Number of matching elements

    Example:
        >>> count = await get_elements_count(page, ".product-item")
        >>> print(f"Found {count} products")
    """
    return await page.locator(selector).count()


async def is_element_visible(page: Page, selector: str) -> bool:
    """
    Check if an element is visible on the page.

    Args:
        page: Playwright page instance
        selector: CSS selector

    Returns:
        bool: True if element is visible

    Example:
        >>> if await is_element_visible(page, "#error-message"):
        >>>     print("Error message is displayed")
    """
    try:
        element = page.locator(selector)
        return await element.is_visible()
    except Exception:
        return False


async def wait_for_page_load(page: Page, timeout: int | None = None) -> None:
    """
    Wait for page to be fully loaded.

    This waits for the 'load' event and ensures the network is idle.

    Args:
        page: Playwright page instance
        timeout: Maximum time to wait in milliseconds

    Example:
        >>> await page.goto(url)
        >>> await wait_for_page_load(page)
    """
    if timeout is None:
        timeout = settings.test.page_load_timeout

    await page.wait_for_load_state("load", timeout=timeout)
    await page.wait_for_load_state("networkidle", timeout=timeout)
    logger.debug("Page fully loaded")


def create_test_data_file(
    filename: str,
    data: dict[str, Any],
) -> Path:
    """
    Create a test data file (for temporary test data).

    Args:
        filename: Name of the file to create
        data: Data to write (will be converted to JSON)

    Returns:
        Path: Path to created file

    Example:
        >>> test_data = {"user": "test@example.com", "password": "secret"}
        >>> file_path = create_test_data_file("test_user.json", test_data)
    """
    import json

    data_dir = settings.project_root / "reports" / "test_data"
    data_dir.mkdir(parents=True, exist_ok=True)

    file_path = data_dir / filename

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    logger.info(f"Test data file created: {file_path}")
    return file_path


async def highlight_element(
    page: Page,
    selector: str,
    duration: int = 1000,
) -> None:
    """
    Highlight an element on the page (useful for debugging).

    Args:
        page: Playwright page instance
        selector: CSS selector
        duration: How long to highlight in milliseconds

    Example:
        >>> await highlight_element(page, "button#submit", duration=2000)
    """
    # Add temporary highlighting style
    await page.eval_on_selector(
        selector,
        """(element) => {
            element.style.border = '3px solid red';
            element.style.backgroundColor = 'yellow';
        }""",
    )

    # Wait for specified duration
    await asyncio.sleep(duration / 1000)

    # Remove highlighting
    await page.eval_on_selector(
        selector,
        """(element) => {
            element.style.border = '';
            element.style.backgroundColor = '';
        }""",
    )


def get_random_item_from_list(items: list[T]) -> T:
    """
    Get a random item from a list.

    Args:
        items: List of items

    Returns:
        T: Random item from the list

    Example:
        >>> users = ["user1", "user2", "user3"]
        >>> random_user = get_random_item_from_list(users)
    """
    return random.choice(items)


if __name__ == "__main__":
    """
    Module test/demonstration code.

    Run this module directly to see helper functions in action:
        python -m utils.helpers
    """
    print("Helper Utilities Examples")
    print("=" * 80)

    # String utilities
    print(f"Timestamp: {get_timestamp()}")
    print(f"Sanitized: {sanitize_filename('test: file #1.txt')}")
    print(f"Random string: {generate_random_string(12)}")
    print()

    # Data generation
    print(f"Random email: {generate_random_email()}")
    print(f"Random phone: {generate_random_phone()}")
    print(f"Random zipcode: {generate_random_zipcode()}")
    print()

    # Currency formatting
    print(f"Formatted: {format_currency(1234.56)}")
    print(f"Parsed: {parse_currency('$1,234.56')}")
    print()

    # Test user data
    print("Generated test user:")
    user = generate_test_user_data()
    for key, value in user.items():
        print(f"  {key}: {value}")

    print("=" * 80)
