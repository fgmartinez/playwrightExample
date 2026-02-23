"""
Login Page Object
=================
Page object for SauceDemo login page using modern Playwright patterns.
Elements are defined as Locators for clean, chainable interactions.
"""

from playwright.async_api import Page

import logging

from config import UserType, settings
from pages.page_helpers import BasePage, get_text, is_visible_safe

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """Page object for the SauceDemo login page."""

    URL = "/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

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

    async def login_as(self, user_type: UserType) -> None:
        """Login with a predefined user type."""
        username, password = settings.users[user_type]
        await self.login(username, password)

    async def enter_username(self, username: str) -> None:
        """Fill the username field."""
        await self.username_input.fill(username)

    async def enter_password(self, password: str) -> None:
        """Fill the password field."""
        await self.password_input.fill(password)

    async def click_login_button(self) -> None:
        """Click the login button."""
        await self.login_button.click()

    async def clear_form(self) -> None:
        """Clear both username and password fields."""
        await self.username_input.clear()
        await self.password_input.clear()

    async def close_error(self) -> None:
        """Close error message if visible."""
        if await is_visible_safe(self.error_container):
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
        return await is_visible_safe(self.error_container)

    async def get_error_message(self) -> str:
        """Get error message text."""
        if await self.has_error():
            return await get_text(self.error_container)
        return ""

    async def get_username_value(self) -> str:
        """Get current value of the username field."""
        return await self.username_input.input_value()

    async def get_password_value(self) -> str:
        """Get current value of the password field."""
        return await self.password_input.input_value()

    async def is_login_button_enabled(self) -> bool:
        """Check if the login button is enabled."""
        return await self.login_button.is_enabled()

    async def get_login_credentials_list(self) -> dict[str, list[str] | str]:
        """Get the displayed credentials from the login page info panels."""
        usernames_text = await get_text(self.credentials_panel)
        password_text = await get_text(self.password_panel)

        # Parse usernames: the panel has a header line then usernames
        lines = [line.strip() for line in usernames_text.split("\n") if line.strip()]
        # First line is the header "Accepted usernames are:", skip it
        usernames = lines[1:] if len(lines) > 1 else lines

        # Parse password: similar format
        pw_lines = [line.strip() for line in password_text.split("\n") if line.strip()]
        password = pw_lines[-1] if pw_lines else ""

        return {"usernames": usernames, "password": password}

    async def is_loaded(self) -> bool:
        """Check if login page is fully loaded."""
        try:
            await self.username_input.wait_for(state="visible", timeout=5000)
            await self.login_button.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False

