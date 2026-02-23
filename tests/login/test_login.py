"""
Login Tests
===========
Comprehensive test cases for the login functionality of SauceDemo application.

Test Categories:
- @pytest.mark.smoke: Critical path tests
- @pytest.mark.login: All login-related tests
- @pytest.mark.regression: Full regression suite
"""

import pytest
from playwright.async_api import Page, expect

from config import UserType, settings
from pages import LoginPage
import logging

from utils.decorators import log_execution_time

logger = logging.getLogger(__name__)


@pytest.mark.login
@pytest.mark.smoke
class TestLoginSuccess:
    """Test suite for successful login scenarios."""

    @log_execution_time
    async def test_login_with_standard_user(self, page: Page) -> None:
        """Test successful login with standard user credentials."""
        login_page = LoginPage(page)
        await login_page.navigate()
        await expect(login_page.username_input).to_be_visible()
        await expect(login_page.password_input).to_be_visible()
        await expect(login_page.login_button).to_be_visible()

        await login_page.login(
            settings.standard_user,
            settings.standard_password,
        )

        assert await login_page.is_login_successful(), "Login should be successful"
        await expect(page).to_have_url(f"{settings.base_url}/inventory.html")
        logger.info("Standard user logged in successfully")

    async def test_login_with_problem_user(self, page: Page) -> None:
        """Test login with problem user (user with UI issues)."""
        login_page = LoginPage(page)
        await login_page.navigate()

        await login_page.login_as(UserType.PROBLEM)

        assert await login_page.is_login_successful(), "Problem user should be able to login"
        logger.info("Problem user logged in successfully")

    async def test_login_with_performance_glitch_user(self, page: Page) -> None:
        """Test login with performance glitch user (slow response)."""
        login_page = LoginPage(page)
        await login_page.navigate()

        await login_page.login_as(UserType.PERFORMANCE)
        await page.wait_for_timeout(2000)

        assert await login_page.is_login_successful(), (
            "Performance glitch user should be able to login"
        )
        logger.info("Performance glitch user logged in successfully")

    async def test_login_preserves_entered_username(self, page: Page) -> None:
        """Test that username field preserves entered value."""
        login_page = LoginPage(page)
        await login_page.navigate()

        test_username = "test_user"
        await login_page.enter_username(test_username)

        entered_value = await login_page.get_username_value()
        assert entered_value == test_username, "Username should be preserved in field"
        logger.info("Username field preserves entered value")


@pytest.mark.login
@pytest.mark.smoke
class TestLoginFailure:
    """Test suite for login failure scenarios."""

    async def test_login_with_locked_out_user(self, page: Page) -> None:
        """Test login attempt with locked out user."""
        login_page = LoginPage(page)
        await login_page.navigate()

        await login_page.login_as(UserType.LOCKED)

        assert await login_page.has_error(), "Error message should be displayed"

        error_message = await login_page.get_error_message()
        assert "locked out" in error_message.lower(), (
            f"Error should mention locked out user, got: {error_message}"
        )

        assert not await login_page.is_login_successful(), "Login should not succeed"
        logger.info("Locked out user correctly prevented from logging in")

    async def test_login_with_invalid_username(self, page: Page) -> None:
        """Test login attempt with invalid username."""
        login_page = LoginPage(page)
        await login_page.navigate()

        await login_page.login("invalid_user", settings.standard_password)

        assert await login_page.has_error(), "Error message should be displayed"

        error_message = await login_page.get_error_message()
        assert "username" in error_message.lower() or "password" in error_message.lower(), (
            f"Error should mention invalid credentials, got: {error_message}"
        )
        logger.info("Invalid username correctly rejected")

    async def test_login_with_invalid_password(self, page: Page) -> None:
        """Test login attempt with invalid password."""
        login_page = LoginPage(page)
        await login_page.navigate()

        await login_page.login(settings.standard_user, "wrong_password")

        assert await login_page.has_error(), "Error message should be displayed"

        error_message = await login_page.get_error_message()
        assert "password" in error_message.lower() or "username" in error_message.lower(), (
            f"Error should mention invalid credentials, got: {error_message}"
        )
        logger.info("Invalid password correctly rejected")

    async def test_login_with_empty_username(self, page: Page) -> None:
        """Test login attempt with empty username."""
        login_page = LoginPage(page)
        await login_page.navigate()

        await login_page.enter_username("")
        await login_page.enter_password(settings.standard_password)
        await login_page.click_login_button()

        assert await login_page.has_error(), "Error message should be displayed"

        error_message = await login_page.get_error_message()
        assert "username" in error_message.lower() and "required" in error_message.lower(), (
            f"Error should mention required username, got: {error_message}"
        )
        logger.info("Empty username correctly rejected")

    async def test_login_with_empty_password(self, page: Page) -> None:
        """Test login attempt with empty password."""
        login_page = LoginPage(page)
        await login_page.navigate()

        await login_page.enter_username(settings.standard_user)
        await login_page.enter_password("")
        await login_page.click_login_button()

        assert await login_page.has_error(), "Error message should be displayed"

        error_message = await login_page.get_error_message()
        assert "password" in error_message.lower() and "required" in error_message.lower(), (
            f"Error should mention required password, got: {error_message}"
        )
        logger.info("Empty password correctly rejected")

    async def test_login_with_empty_credentials(self, page: Page) -> None:
        """Test login attempt with both fields empty."""
        login_page = LoginPage(page)
        await login_page.navigate()

        await login_page.click_login_button()

        assert await login_page.has_error(), "Error message should be displayed"

        error_message = await login_page.get_error_message()
        assert "username" in error_message.lower() and "required" in error_message.lower(), (
            f"Error should mention required field, got: {error_message}"
        )
        logger.info("Empty credentials correctly rejected")


@pytest.mark.login
class TestLoginUI:
    """Test suite for login page UI elements and interactions."""

    async def test_login_page_elements_visible(self, page: Page) -> None:
        """Test that all login page elements are visible."""
        login_page = LoginPage(page)
        await login_page.navigate()

        assert await login_page.is_loaded(), "Login page should be fully loaded"
        await expect(login_page.username_input).to_be_visible()
        await expect(login_page.password_input).to_be_visible()
        await expect(login_page.login_button).to_be_visible()
        logger.info("All login page elements are visible")

    async def test_login_button_enabled(self, page: Page) -> None:
        """Test that login button is enabled by default."""
        login_page = LoginPage(page)
        await login_page.navigate()

        assert await login_page.is_login_button_enabled(), "Login button should be enabled"
        logger.info("Login button is enabled")

    async def test_error_message_can_be_dismissed(self, page: Page) -> None:
        """Test that error messages can be dismissed."""
        login_page = LoginPage(page)
        await login_page.navigate()

        await login_page.click_login_button()
        assert await login_page.has_error(), "Error should be displayed"

        await login_page.close_error()

        assert not await login_page.has_error(), "Error should be dismissed"
        logger.info("Error message can be dismissed")

    async def test_credentials_list_displayed(self, page: Page) -> None:
        """Test that accepted credentials list is displayed."""
        login_page = LoginPage(page)
        await login_page.navigate()

        credentials = await login_page.get_login_credentials_list()

        assert len(credentials["usernames"]) > 0, "Should display accepted usernames"
        assert len(credentials["password"]) > 0, "Should display password"
        logger.info(f"Found {len(credentials['usernames'])} accepted usernames")

    async def test_clear_fields_functionality(self, page: Page) -> None:
        """Test clearing input fields."""
        login_page = LoginPage(page)
        await login_page.navigate()

        await login_page.enter_username("test_user")
        await login_page.enter_password("test_password")

        await login_page.clear_form()

        username = await login_page.get_username_value()
        password = await login_page.get_password_value()

        assert username == "", "Username field should be empty"
        assert password == "", "Password field should be empty"
        logger.info("Fields can be cleared successfully")


@pytest.mark.login
@pytest.mark.regression
class TestLoginEdgeCases:
    """Test suite for login edge cases and boundary conditions."""

    async def test_login_with_special_characters_in_username(self, page: Page) -> None:
        """Test login with special characters in username."""
        login_page = LoginPage(page)
        await login_page.navigate()

        await login_page.login("user@#$%", settings.standard_password)

        assert await login_page.has_error(), "Error should be displayed for invalid username"
        logger.info("Special characters in username handled correctly")

    async def test_login_case_sensitivity(self, page: Page) -> None:
        """Test that login is case-sensitive."""
        login_page = LoginPage(page)
        await login_page.navigate()

        uppercase_username = settings.standard_user.upper()
        await login_page.login(uppercase_username, settings.standard_password)

        assert await login_page.has_error(), "Login should fail with different case"
        logger.info("Login is case-sensitive")

    async def test_multiple_failed_login_attempts(self, page: Page) -> None:
        """Test multiple failed login attempts."""
        login_page = LoginPage(page)
        await login_page.navigate()

        for i in range(3):
            await login_page.clear_form()
            await login_page.login("invalid_user", "wrong_password")

            assert await login_page.has_error(), (
                f"Error should be displayed on attempt {i + 1}"
            )

            if i < 2:
                await login_page.close_error()

        logger.info("Multiple failed attempts handled correctly")
