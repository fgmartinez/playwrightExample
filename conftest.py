"""
============================================================================
Pytest Configuration and Global Fixtures
============================================================================
This is the root conftest.py file that provides global fixtures and
configuration for the entire test suite. It's automatically discovered
by pytest and makes fixtures available to all tests.

Key Features:
- Browser and context fixtures
- Authentication state management
- Logging setup
- Test hooks for reporting
- Allure integration
- Custom markers

Architecture:
- Fixtures use dependency injection pattern
- Scope management for resource optimization
- Automatic cleanup with yield fixtures
- Integration with Playwright pytest plugin

Usage:
    # Fixtures are automatically available in tests
    def test_example(page, logged_in_user):
        # 'page' and 'logged_in_user' are fixtures
        page.goto("/dashboard")

Author: Your Name
Created: 2026-01-23
============================================================================
"""

import asyncio
from pathlib import Path
from typing import Any, AsyncGenerator, Generator

import pytest
from playwright.async_api import Browser, BrowserContext, Page, Playwright
from pytest import Config, Item, StashKey

from config import settings
import logging

logger = logging.getLogger(__name__)

# Stash keys for sharing data between hooks
phase_key = StashKey[dict[str, Any]]()


def pytest_configure(config: Config) -> None:
    """
    Pytest hook called after command line options have been parsed.

    This hook is called once at the start of the test session to perform
    initial setup and configuration.

    Args:
        config: Pytest configuration object
    """
    # Setup colored logging
    import colorlog
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    ))
    logging.basicConfig(handlers=[handler], level=logging.INFO)
    for noisy in ("playwright", "asyncio", "urllib3", "filelock"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    logger.info("=" * 80)
    logger.info("Test Session Started")
    logger.info("=" * 80)
    logger.info(f"Environment: {settings.env}")
    logger.info(f"Base URL: {settings.base_url}")
    logger.info(f"Browser: {settings.browser.browser}")
    logger.info(f"Headless: {settings.browser.headless}")
    logger.info("=" * 80)

    # Create necessary directories
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    settings.logs_dir.mkdir(parents=True, exist_ok=True)


def pytest_collection_finish(session: Any) -> None:
    """
    Pytest hook called after test collection has been performed.

    Args:
        session: Pytest session object
    """
    logger.info(f"Collected {len(session.items)} test(s)")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: Item, call: Any) -> Generator[None, Any, None]:
    """
    Pytest hook to process test execution results.

    This hook is called after each phase of test execution (setup, call, teardown)
    and is used for custom reporting and screenshot capture on failures.

    Args:
        item: Test item being executed
        call: Test call information
    """
    outcome = yield
    report = outcome.get_result()

    # Store test results in item stash for access in fixtures
    if report.when == "call":
        item.stash[phase_key] = {"report": report}

        # Log test results
        if report.passed:
            logger.info(f"✓ PASSED: {item.nodeid}")
        elif report.failed:
            logger.error(f"✗ FAILED: {item.nodeid}")
            logger.error(f"Error: {report.longreprtext}")
        elif report.skipped:
            logger.warning(f"⊘ SKIPPED: {item.nodeid}")


def pytest_sessionfinish(session: Any, exitstatus: int) -> None:
    """
    Pytest hook called after whole test session has finished.

    Args:
        session: Pytest session object
        exitstatus: Exit status code
    """
    logger.info("=" * 80)
    logger.info("Test Session Finished")
    logger.info(f"Exit Status: {exitstatus}")
    logger.info("=" * 80)


# ============================================================================
# Browser Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def browser_type_launch_args() -> dict[str, Any]:
    """
    Provide launch arguments for the browser.

    This fixture returns a dictionary of arguments passed to browser.launch().
    Customize this to add proxy settings, custom flags, etc.

    Returns:
        dict[str, Any]: Browser launch arguments

    Example:
        >>> def browser_type_launch_args():
        >>>     return {
        >>>         "headless": True,
        >>>         "slow_mo": 100,
        >>>         "args": ["--start-maximized"]
        >>>     }
    """
    launch_args = {
        "headless": settings.browser.headless,
        "slow_mo": settings.browser.slow_mo,
    }

    # Add additional arguments for Chromium
    if settings.browser.browser == "chromium":
        launch_args["args"] = [
            "--disable-blink-features=AutomationControlled",  # Avoid detection
            "--no-sandbox",  # Required in some CI environments
        ]

    logger.debug(f"Browser launch args: {launch_args}")
    return launch_args


@pytest.fixture(scope="session")
def browser_context_args() -> dict[str, Any]:
    """
    Provide context arguments for browser context creation.

    This fixture returns arguments passed to browser.new_context().
    Used for viewport size, user agent, permissions, etc.

    Returns:
        dict[str, Any]: Browser context arguments
    """
    context_args: dict[str, Any] = {
        "viewport": {
            "width": settings.browser.viewport_width,
            "height": settings.browser.viewport_height,
        },
        "ignore_https_errors": settings.browser.ignore_https_errors,
        "accept_downloads": settings.browser.accept_downloads,
    }

    # Add user agent if specified
    if settings.browser.user_agent:
        context_args["user_agent"] = settings.browser.user_agent

    # Mobile emulation
    if settings.browser.mobile_emulation and settings.browser.device_name:
        # Note: Device emulation is handled by playwright's device_name parameter
        context_args["device_name"] = settings.browser.device_name

    logger.debug(f"Browser context args: {context_args}")
    return context_args


# Note: We use pytest-playwright's built-in page and context fixtures
# The browser_type_launch_args and browser_context_args fixtures above
# are automatically used by pytest-playwright to configure the browser


# ============================================================================
# Authentication Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def auth_state_file() -> Path:
    """
    Provide path to authentication state storage file.

    Returns:
        Path: Path to auth state JSON file
    """
    auth_dir = settings.project_root / "playwright" / ".auth"
    auth_dir.mkdir(parents=True, exist_ok=True)
    return auth_dir / "user.json"


@pytest.fixture(scope="session")
async def authenticated_context(
    playwright: Playwright,
    browser_type_launch_args: dict[str, Any],
    browser_context_args: dict[str, Any],
    auth_state_file: Path,
) -> AsyncGenerator[BrowserContext, None]:
    """
    Provide a browser context with authentication state persisted.

    This fixture logs in once per session and saves the authentication state,
    then reuses it for all tests that need authentication. This significantly
    speeds up test execution.

    Args:
        playwright: Playwright instance
        browser_type_launch_args: Browser launch arguments
        browser_context_args: Context arguments
        auth_state_file: Path to store auth state

    Yields:
        BrowserContext: Authenticated browser context

    Example:
        >>> async def test_dashboard(authenticated_context):
        >>>     page = await authenticated_context.new_page()
        >>>     await page.goto("/dashboard")
        >>>     # User is already logged in
    """
    # Launch browser
    browser = await playwright.chromium.launch(**browser_type_launch_args)

    # Check if auth state already exists
    if auth_state_file.exists():
        logger.info("Loading existing authentication state")
        context = await browser.new_context(
            **browser_context_args, storage_state=str(auth_state_file)
        )
    else:
        logger.info("Creating new authentication state")
        context = await browser.new_context(**browser_context_args)

        # Perform login
        page = await context.new_page()
        await page.goto(settings.base_url)

        # Login with standard user
        await page.fill("#user-name", settings.standard_user)
        await page.fill("#password", settings.standard_password)
        await page.click("#login-button")

        # Wait for successful login (inventory page)
        await page.wait_for_url("**/inventory.html")

        # Save authentication state
        await context.storage_state(path=str(auth_state_file))
        logger.info(f"Authentication state saved: {auth_state_file}")

        await page.close()

    yield context

    await context.close()
    await browser.close()


@pytest.fixture(scope="function")
async def logged_in_page(authenticated_context: BrowserContext) -> AsyncGenerator[Page, None]:
    """
    Provide a page with user already logged in.

    This is a convenience fixture for tests that require authentication.
    It reuses the authenticated context for better performance.

    Args:
        authenticated_context: Authenticated browser context

    Yields:
        Page: Page instance with user logged in

    Example:
        >>> async def test_products(logged_in_page):
        >>>     # User is already logged in
        >>>     await logged_in_page.goto(f"{settings.base_url}/inventory.html")
        >>>     products = await logged_in_page.locator(".inventory_item").count()
        >>>     assert products > 0
    """
    page = await authenticated_context.new_page()
    page.set_default_timeout(settings.test.default_timeout)

    # Navigate to inventory page (logged in state)
    await page.goto(f"{settings.base_url}/inventory.html")

    yield page

    await page.close()


# ============================================================================
# API Testing Fixtures
# ============================================================================


@pytest.fixture(scope="session")
async def api_request_context(playwright: Playwright) -> AsyncGenerator[Any, None]:
    """
    Provide an API request context for API testing.

    Playwright's APIRequestContext allows making HTTP requests with the
    same session/cookies as browser contexts.

    Args:
        playwright: Playwright instance

    Yields:
        APIRequestContext: API request context

    Example:
        >>> async def test_api(api_request_context):
        >>>     response = await api_request_context.get(f"{settings.api_base_url}/api/data")
        >>>     assert response.ok
        >>>     data = await response.json()
    """
    context = await playwright.request.new_context(
        base_url=settings.api_base_url,
        timeout=settings.api_timeout,
        extra_http_headers={
            "Accept": "application/json",
        },
    )

    yield context

    await context.dispose()


# ============================================================================
# Data Fixtures
# ============================================================================


@pytest.fixture(scope="function")
def test_user_credentials() -> dict[str, str]:
    """
    Provide test user credentials.

    Returns:
        dict[str, str]: Dictionary with username and password

    Example:
        >>> def test_login(page, test_user_credentials):
        >>>     await page.fill("#user-name", test_user_credentials["username"])
        >>>     await page.fill("#password", test_user_credentials["password"])
    """
    return {
        "username": settings.standard_user,
        "password": settings.standard_password,
    }


@pytest.fixture(scope="function")
def test_users_list() -> list[dict[str, str]]:
    """
    Provide a list of test users for data-driven testing.

    Returns:
        list[dict[str, str]]: List of user credentials

    Example:
        >>> @pytest.mark.parametrize("user", test_users_list)
        >>> def test_multi_user_login(page, user):
        >>>     await page.fill("#user-name", user["username"])
    """
    return [
        {"username": settings.standard_user, "password": settings.default_password},
        {"username": settings.problem_user, "password": settings.default_password},
        {"username": settings.performance_glitch_user, "password": settings.default_password},
    ]


# ============================================================================
# Utility Fixtures
# ============================================================================


@pytest.fixture(scope="function")
def test_id(request: pytest.FixtureRequest) -> str:
    """
    Provide unique test identifier.

    Args:
        request: Pytest request fixture

    Returns:
        str: Unique test identifier

    Example:
        >>> def test_example(test_id):
        >>>     logger.info(f"Running test: {test_id}")
    """
    return request.node.nodeid


@pytest.fixture(autouse=True)
def log_test_info(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    """
    Automatically log test start and finish for all tests.

    This fixture uses autouse=True to automatically wrap every test with
    logging information.

    Args:
        request: Pytest request fixture
    """
    test_name = request.node.name
    logger.info(f"▶ Starting test: {test_name}")

    yield

    logger.info(f"■ Finished test: {test_name}")


# ============================================================================
# Marker-based Fixtures
# ============================================================================


@pytest.fixture(scope="function")
def mobile_page(playwright: Playwright, browser_type_launch_args: dict[str, Any]) -> AsyncGenerator[Page, None]:
    """
    Provide a page emulating a mobile device.

    This fixture is used with tests marked with @pytest.mark.mobile.

    Args:
        playwright: Playwright instance
        browser_type_launch_args: Browser launch arguments

    Yields:
        Page: Page with mobile emulation

    Example:
        >>> @pytest.mark.mobile
        >>> async def test_mobile_view(mobile_page):
        >>>     await mobile_page.goto("/")
        >>>     # Page is emulating iPhone 13
    """
    async def _mobile_page() -> AsyncGenerator[Page, None]:
        # Get device configuration
        device = playwright.devices.get(settings.browser.device_name or "iPhone 13")

        browser = await playwright.chromium.launch(**browser_type_launch_args)
        context = await browser.new_context(**device)
        page = await context.new_page()

        yield page

        await context.close()
        await browser.close()

    return _mobile_page()  # type: ignore
