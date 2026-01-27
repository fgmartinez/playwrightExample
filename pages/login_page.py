"""
Login Page Object
=================
Page object for SauceDemo login page using modern Playwright patterns.
Elements are defined as Locators for clean, chainable interactions.
"""

from playwright.async_api import Page

from config import settings
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class LoginPage(BasePage):
    """Page object for the SauceDemo login page."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.url = "/"

        # Form elements - using get_by_test_id for stability
        self.username_input = page.get_by_test_id("username")
        self.password_input = page.get_by_test_id("password")
        self.login_button = page.get_by_test_id("login-button")

        # Error elements
        self.error_container = page.get_by_test_id("error")
        self.error_close_button = page.locator(".error-button")

        # Info panels
        self.credentials_panel = page.locator("#login_credentials")
        self.password_panel = page.locator(".login_password")

    # ========================================================================
    # Actions
    # ========================================================================

    async def login(self, username: str, password: str) -> None:
        """
        Perform login with given credentials.

        Args:
            username: Username to login with
            password: Password to login with
        """
        logger.info(f"Logging in as: {username}")
        await self.username_input.fill(username)
        await self.password_input.fill(password)
        await self.login_button.click()

    async def login_as_standard_user(self) -> None:
        """Login with standard test user."""
        await self.login(settings.standard_user, settings.standard_password)

    async def login_as_locked_user(self) -> None:
        """Attempt login with locked out user (negative test)."""
        await self.login(settings.locked_out_user, settings.default_password)

    async def login_as_problem_user(self) -> None:
        """Login with problem user (UI glitches)."""
        await self.login(settings.problem_user, settings.default_password)

    async def login_as_performance_user(self) -> None:
        """Login with performance glitch user (slow responses)."""
        await self.login(settings.performance_glitch_user, settings.default_password)

    async def clear_form(self) -> None:
        """Clear both username and password fields."""
        await self.username_input.clear()
        await self.password_input.clear()

    async def close_error(self) -> None:
        """Close error message if visible."""
        if await self.is_visible_safe(self.error_container):
            await self.error_close_button.click()

    # ========================================================================
    # State Checks
    # ========================================================================

    async def is_login_successful(self) -> bool:
        """Check if login succeeded by verifying redirect to inventory."""
        try:
            await self.page.wait_for_url("**/inventory.html", timeout=5000)
            logger.info("Login successful")
            return True
        except Exception:
            logger.warning("Login failed or timed out")
            return False

    async def has_error(self) -> bool:
        """Check if error message is displayed."""
        return await self.is_visible_safe(self.error_container)

    async def get_error_message(self) -> str:
        """Get error message text."""
        if await self.has_error():
            return await self.get_text(self.error_container)
        return ""

    async def is_loaded(self) -> bool:
        """Check if login page is fully loaded."""
        try:
            await self.username_input.wait_for(state="visible", timeout=5000)
            await self.login_button.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False

    # ========================================================================
    # Assertions
    # ========================================================================

    async def assert_displayed(self) -> None:
        """Assert login page is displayed with all elements."""
        await self.assert_visible(self.username_input)
        await self.assert_visible(self.password_input)
        await self.assert_visible(self.login_button)
        logger.debug("Login page displayed correctly")

    async def assert_error_contains(self, text: str) -> None:
        """Assert error message contains expected text."""
        error = await self.get_error_message()
        assert text.lower() in error.lower(), f"Expected '{text}' in error: '{error}'"
