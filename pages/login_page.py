"""
============================================================================
Login Page Object
============================================================================
This module defines the LoginPage class, which encapsulates all interactions
with the SauceDemo login page.

Page URL: https://www.saucedemo.com/
Features:
- User authentication
- Error message handling
- Support for different user types
- Credential validation

Usage:
    login_page = LoginPage(page)
    await login_page.navigate()
    await login_page.login("standard_user", "secret_sauce")
    assert await login_page.is_login_successful()

Author: Your Name
Created: 2026-01-23
============================================================================
"""

from playwright.async_api import Page

from config import settings
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class LoginPage(BasePage):
    """
    Page Object for SauceDemo Login Page.

    This class provides methods to interact with the login page, including
    logging in with different user types, handling errors, and verifying
    login state.

    Attributes:
        url: Login page URL path
        username_input: Username input field selector
        password_input: Password input field selector
        login_button: Login button selector
        error_message: Error message container selector
        error_button: Error close button selector
    """

    def __init__(self, page: Page) -> None:
        """
        Initialize the LoginPage.

        Args:
            page: Playwright page instance
        """
        super().__init__(page)
        self.url = "/"

        # Selectors - Using data-test attributes for stability
        self.username_input = '[data-test="username"]'
        self.password_input = '[data-test="password"]'
        self.login_button = '[data-test="login-button"]'
        self.error_message = '[data-test="error"]'
        self.error_button = '.error-button'

        # Alternative selectors using IDs (fallback)
        self.username_input_id = "#user-name"
        self.password_input_id = "#password"
        self.login_button_id = "#login-button"

        logger.debug("LoginPage initialized")

    # ========================================================================
    # Login Actions
    # ========================================================================

    async def enter_username(self, username: str) -> None:
        """
        Enter username into the username field.

        Args:
            username: Username to enter

        Example:
            >>> await login_page.enter_username("standard_user")
        """
        logger.info(f"Entering username: {username}")
        await self.fill(self.username_input, username)

    async def enter_password(self, password: str) -> None:
        """
        Enter password into the password field.

        Args:
            password: Password to enter (will be masked in logs)

        Example:
            >>> await login_page.enter_password("secret_sauce")
        """
        logger.info("Entering password: ****")
        await self.fill(self.password_input, password)

    async def click_login_button(self) -> None:
        """
        Click the login button.

        Example:
            >>> await login_page.click_login_button()
        """
        logger.info("Clicking login button")
        await self.click(self.login_button)

    async def login(self, username: str, password: str) -> None:
        """
        Perform complete login flow.

        This is the main method for logging in. It enters credentials
        and clicks the login button.

        Args:
            username: Username to login with
            password: Password to login with

        Example:
            >>> await login_page.login("standard_user", "secret_sauce")
        """
        logger.info(f"Logging in with username: {username}")
        await self.enter_username(username)
        await self.enter_password(password)
        await self.click_login_button()

        # Wait a moment for the navigation/error to appear
        await self.page.wait_for_timeout(500)

    async def login_with_standard_user(self) -> None:
        """
        Login using the standard test user from configuration.

        This is a convenience method for the most common test scenario.

        Example:
            >>> await login_page.login_with_standard_user()
        """
        await self.login(settings.standard_user, settings.standard_password)

    async def login_with_locked_user(self) -> None:
        """
        Attempt login with locked out user (for negative testing).

        Example:
            >>> await login_page.login_with_locked_user()
            >>> assert await login_page.is_error_displayed()
        """
        await self.login(settings.locked_out_user, settings.default_password)

    async def login_with_problem_user(self) -> None:
        """
        Login with problem user (user with UI issues).

        Example:
            >>> await login_page.login_with_problem_user()
        """
        await self.login(settings.problem_user, settings.default_password)

    async def login_with_performance_glitch_user(self) -> None:
        """
        Login with performance glitch user (slow response times).

        Example:
            >>> await login_page.login_with_performance_glitch_user()
        """
        await self.login(
            settings.performance_glitch_user,
            settings.default_password,
        )

    # ========================================================================
    # Verification Methods
    # ========================================================================

    async def is_login_successful(self) -> bool:
        """
        Check if login was successful by verifying URL change.

        Returns:
            bool: True if redirected to inventory page

        Example:
            >>> success = await login_page.is_login_successful()
            >>> assert success, "Login failed"
        """
        try:
            # Successful login redirects to inventory page
            await self.wait_for_url("**/inventory.html", timeout=5000)
            logger.info("Login successful - redirected to inventory page")
            return True
        except Exception as e:
            logger.warning(f"Login may have failed: {e}")
            return False

    async def is_error_displayed(self) -> bool:
        """
        Check if an error message is displayed.

        Returns:
            bool: True if error message is visible

        Example:
            >>> if await login_page.is_error_displayed():
            >>>     error_text = await login_page.get_error_message()
            >>>     print(f"Error: {error_text}")
        """
        return await self.is_visible(self.error_message)

    async def get_error_message(self) -> str:
        """
        Get the error message text.

        Returns:
            str: Error message text

        Example:
            >>> error = await login_page.get_error_message()
            >>> assert "locked out" in error.lower()
        """
        if await self.is_error_displayed():
            error_text = await self.get_text(self.error_message)
            logger.info(f"Error message: {error_text}")
            return error_text
        return ""

    async def close_error_message(self) -> None:
        """
        Close the error message by clicking the X button.

        Example:
            >>> await login_page.close_error_message()
            >>> assert not await login_page.is_error_displayed()
        """
        if await self.is_error_displayed():
            logger.info("Closing error message")
            await self.click(self.error_button)

    async def is_login_button_enabled(self) -> bool:
        """
        Check if the login button is enabled.

        Returns:
            bool: True if login button is enabled

        Example:
            >>> enabled = await login_page.is_login_button_enabled()
        """
        return await self.is_enabled(self.login_button)

    # ========================================================================
    # Field Validation
    # ========================================================================

    async def clear_username(self) -> None:
        """
        Clear the username field.

        Example:
            >>> await login_page.clear_username()
        """
        logger.debug("Clearing username field")
        await self.page.fill(self.username_input, "")

    async def clear_password(self) -> None:
        """
        Clear the password field.

        Example:
            >>> await login_page.clear_password()
        """
        logger.debug("Clearing password field")
        await self.page.fill(self.password_input, "")

    async def clear_all_fields(self) -> None:
        """
        Clear both username and password fields.

        Example:
            >>> await login_page.clear_all_fields()
        """
        await self.clear_username()
        await self.clear_password()

    async def get_username_value(self) -> str:
        """
        Get the current value in the username field.

        Returns:
            str: Current username field value

        Example:
            >>> username = await login_page.get_username_value()
        """
        value = await self.get_attribute(self.username_input, "value")
        return value or ""

    async def get_password_value(self) -> str:
        """
        Get the current value in the password field.

        Returns:
            str: Current password field value

        Example:
            >>> password = await login_page.get_password_value()
        """
        value = await self.get_attribute(self.password_input, "value")
        return value or ""

    # ========================================================================
    # Page State Checks
    # ========================================================================

    async def is_page_loaded(self) -> bool:
        """
        Verify that the login page is fully loaded.

        Returns:
            bool: True if all key elements are present

        Example:
            >>> await login_page.navigate()
            >>> assert await login_page.is_page_loaded()
        """
        try:
            await self.wait_for_selector(self.username_input, state="visible", timeout=5000)
            await self.wait_for_selector(self.password_input, state="visible", timeout=5000)
            await self.wait_for_selector(self.login_button, state="visible", timeout=5000)
            logger.debug("Login page fully loaded")
            return True
        except Exception as e:
            logger.error(f"Login page not fully loaded: {e}")
            return False

    async def get_login_credentials_list(self) -> dict[str, list[str]]:
        """
        Get the list of accepted usernames and password from the page.

        SauceDemo displays accepted credentials on the login page.

        Returns:
            dict[str, list[str]]: Dictionary with 'usernames' and 'password'

        Example:
            >>> credentials = await login_page.get_login_credentials_list()
            >>> print(credentials['usernames'])
            ['standard_user', 'locked_out_user', ...]
        """
        # This is specific to SauceDemo which shows credentials on the page
        try:
            # Get the credentials text from the page
            credentials_div = "#login_credentials"
            password_div = ".login_password"

            usernames_text = await self.get_text(credentials_div)
            password_text = await self.get_text(password_div)

            # Parse usernames (skip first line which is the header)
            usernames = [
                line.strip()
                for line in usernames_text.split("\n")[1:]
                if line.strip() and line.strip() != "Accepted usernames are:"
            ]

            # Parse password (skip first line which is the header)
            password_line = password_text.split("\n")[1].strip() if len(password_text.split("\n")) > 1 else ""

            logger.debug(f"Found {len(usernames)} accepted usernames")
            return {
                "usernames": usernames,
                "password": [password_line] if password_line else [],
            }
        except Exception as e:
            logger.error(f"Could not parse credentials list: {e}")
            return {"usernames": [], "password": []}

    # ========================================================================
    # Assertions
    # ========================================================================

    async def assert_login_page_displayed(self) -> None:
        """
        Assert that the login page is displayed.

        Raises:
            AssertionError: If login page elements are not visible

        Example:
            >>> await login_page.navigate()
            >>> await login_page.assert_login_page_displayed()
        """
        await self.assert_element_visible(self.username_input)
        await self.assert_element_visible(self.password_input)
        await self.assert_element_visible(self.login_button)
        logger.debug("Login page is displayed correctly")

    async def assert_error_message_contains(self, expected_text: str) -> None:
        """
        Assert that the error message contains expected text.

        Args:
            expected_text: Text that should be in the error message

        Raises:
            AssertionError: If error message doesn't contain expected text

        Example:
            >>> await login_page.assert_error_message_contains("locked out")
        """
        error_text = await self.get_error_message()
        assert expected_text.lower() in error_text.lower(), (
            f"Expected error message to contain '{expected_text}', "
            f"but got: '{error_text}'"
        )
        logger.debug(f"Error message contains expected text: {expected_text}")
