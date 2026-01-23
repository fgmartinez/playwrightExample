"""
============================================================================
Login Tests
============================================================================
This module contains comprehensive test cases for the login functionality
of SauceDemo application.

Test Coverage:
- Successful login with valid credentials
- Login failure with invalid credentials
- Locked out user handling
- Empty field validation
- Error message display and dismissal
- Login button state

Test Categories:
- @pytest.mark.smoke: Critical path tests
- @pytest.mark.login: All login-related tests
- @pytest.mark.regression: Full regression suite

Author: Your Name
Created: 2026-01-23
============================================================================
"""

import pytest
from playwright.async_api import Page, expect

from config import settings
from pages import LoginPage
from utils.decorators import log_execution_time
from utils.logger import get_logger

logger = get_logger(__name__)


@pytest.mark.login
@pytest.mark.smoke
class TestLoginSuccess:
    """
    Test suite for successful login scenarios.

    These tests verify that users can successfully log in with valid
    credentials and are redirected to the inventory page.
    """

    @log_execution_time
    async def test_login_with_standard_user(self, page: Page) -> None:
        """
        Test successful login with standard user credentials.

        Steps:
            1. Navigate to login page
            2. Enter valid username and password
            3. Click login button
            4. Verify redirect to inventory page

        Expected: User is logged in and redirected to /inventory.html
        """
        login_page = LoginPage(page)

        # Navigate to login page
        await login_page.navigate()
        await login_page.assert_login_page_displayed()

        # Perform login
        await login_page.login(
            settings.standard_user,
            settings.standard_password,
        )

        # Verify successful login
        assert await login_page.is_login_successful(), "Login should be successful"
        expect(page).to_have_url(f"{settings.base_url}/inventory.html")

        logger.info("✓ Standard user logged in successfully")

    async def test_login_with_problem_user(self, page: Page) -> None:
        """
        Test login with problem user (user with UI issues).

        Steps:
            1. Navigate to login page
            2. Login with problem user credentials
            3. Verify successful login despite known issues

        Expected: Problem user can log in successfully
        """
        login_page = LoginPage(page)
        await login_page.navigate()

        await login_page.login_with_problem_user()

        assert await login_page.is_login_successful(), "Problem user should be able to login"
        logger.info("✓ Problem user logged in successfully")

    async def test_login_with_performance_glitch_user(self, page: Page) -> None:
        """
        Test login with performance glitch user (slow response).

        Steps:
            1. Navigate to login page
            2. Login with performance glitch user
            3. Wait for login to complete (may take longer)
            4. Verify successful login

        Expected: Login succeeds despite performance delays
        """
        login_page = LoginPage(page)
        await login_page.navigate()

        await login_page.login_with_performance_glitch_user()

        # May need extra time due to performance glitch
        await page.wait_for_timeout(2000)

        assert await login_page.is_login_successful(), "Performance glitch user should be able to login"
        logger.info("✓ Performance glitch user logged in successfully")

    async def test_login_preserves_entered_username(self, page: Page) -> None:
        """
        Test that username field preserves entered value.

        Steps:
            1. Navigate to login page
            2. Enter username
            3. Verify username is displayed in field

        Expected: Username field shows entered value
        """
        login_page = LoginPage(page)
        await login_page.navigate()

        test_username = "test_user"
        await login_page.enter_username(test_username)

        entered_value = await login_page.get_username_value()
        assert entered_value == test_username, "Username should be preserved in field"

        logger.info("✓ Username field preserves entered value")


@pytest.mark.login
@pytest.mark.smoke
class TestLoginFailure:
    """
    Test suite for login failure scenarios.

    These tests verify proper error handling for invalid credentials,
    locked users, and empty fields.
    """

    async def test_login_with_locked_out_user(self, page: Page) -> None:
        """
        Test login attempt with locked out user.

        Steps:
            1. Navigate to login page
            2. Attempt login with locked out user credentials
            3. Verify error message is displayed
            4. Verify user remains on login page

        Expected: Error message displayed, user not logged in
        """
        login_page = LoginPage(page)
        await login_page.navigate()

        await login_page.login_with_locked_user()

        # Verify error message
        assert await login_page.is_error_displayed(), "Error message should be displayed"

        error_message = await login_page.get_error_message()
        assert "locked out" in error_message.lower(), (
            f"Error should mention locked out user, got: {error_message}"
        )

        # Verify still on login page
        assert not await login_page.is_login_successful(), "Login should not succeed"

        logger.info("✓ Locked out user correctly prevented from logging in")

    async def test_login_with_invalid_username(self, page: Page) -> None:
        """
        Test login attempt with invalid username.

        Steps:
            1. Navigate to login page
            2. Enter invalid username and valid password
            3. Click login button
            4. Verify error message is displayed

        Expected: Error message displayed for invalid credentials
        """
        login_page = LoginPage(page)
        await login_page.navigate()

        await login_page.login("invalid_user", settings.standard_password)

        assert await login_page.is_error_displayed(), "Error message should be displayed"

        error_message = await login_page.get_error_message()
        assert "username" in error_message.lower() or "password" in error_message.lower(), (
            f"Error should mention invalid credentials, got: {error_message}"
        )

        logger.info("✓ Invalid username correctly rejected")

    async def test_login_with_invalid_password(self, page: Page) -> None:
        """
        Test login attempt with invalid password.

        Steps:
            1. Navigate to login page
            2. Enter valid username and invalid password
            3. Click login button
            4. Verify error message is displayed

        Expected: Error message displayed for invalid credentials
        """
        login_page = LoginPage(page)
        await login_page.navigate()

        await login_page.login(settings.standard_user, "wrong_password")

        assert await login_page.is_error_displayed(), "Error message should be displayed"

        error_message = await login_page.get_error_message()
        assert "password" in error_message.lower() or "username" in error_message.lower(), (
            f"Error should mention invalid credentials, got: {error_message}"
        )

        logger.info("✓ Invalid password correctly rejected")

    async def test_login_with_empty_username(self, page: Page) -> None:
        """
        Test login attempt with empty username.

        Steps:
            1. Navigate to login page
            2. Leave username empty, enter password
            3. Click login button
            4. Verify error message is displayed

        Expected: Error message displayed for empty username
        """
        login_page = LoginPage(page)
        await login_page.navigate()

        await login_page.enter_username("")
        await login_page.enter_password(settings.standard_password)
        await login_page.click_login_button()

        assert await login_page.is_error_displayed(), "Error message should be displayed"

        error_message = await login_page.get_error_message()
        assert "username" in error_message.lower() and "required" in error_message.lower(), (
            f"Error should mention required username, got: {error_message}"
        )

        logger.info("✓ Empty username correctly rejected")

    async def test_login_with_empty_password(self, page: Page) -> None:
        """
        Test login attempt with empty password.

        Steps:
            1. Navigate to login page
            2. Enter username, leave password empty
            3. Click login button
            4. Verify error message is displayed

        Expected: Error message displayed for empty password
        """
        login_page = LoginPage(page)
        await login_page.navigate()

        await login_page.enter_username(settings.standard_user)
        await login_page.enter_password("")
        await login_page.click_login_button()

        assert await login_page.is_error_displayed(), "Error message should be displayed"

        error_message = await login_page.get_error_message()
        assert "password" in error_message.lower() and "required" in error_message.lower(), (
            f"Error should mention required password, got: {error_message}"
        )

        logger.info("✓ Empty password correctly rejected")

    async def test_login_with_empty_credentials(self, page: Page) -> None:
        """
        Test login attempt with both fields empty.

        Steps:
            1. Navigate to login page
            2. Leave both username and password empty
            3. Click login button
            4. Verify error message is displayed

        Expected: Error message displayed for empty fields
        """
        login_page = LoginPage(page)
        await login_page.navigate()

        await login_page.click_login_button()

        assert await login_page.is_error_displayed(), "Error message should be displayed"

        error_message = await login_page.get_error_message()
        assert "username" in error_message.lower() and "required" in error_message.lower(), (
            f"Error should mention required field, got: {error_message}"
        )

        logger.info("✓ Empty credentials correctly rejected")


@pytest.mark.login
class TestLoginUI:
    """
    Test suite for login page UI elements and interactions.

    These tests verify the presence and behavior of UI elements on the
    login page.
    """

    async def test_login_page_elements_visible(self, page: Page) -> None:
        """
        Test that all login page elements are visible.

        Steps:
            1. Navigate to login page
            2. Verify all key elements are present

        Expected: All login form elements are visible
        """
        login_page = LoginPage(page)
        await login_page.navigate()

        # Verify all elements are visible
        assert await login_page.is_page_loaded(), "Login page should be fully loaded"
        await login_page.assert_login_page_displayed()

        logger.info("✓ All login page elements are visible")

    async def test_login_button_enabled(self, page: Page) -> None:
        """
        Test that login button is enabled by default.

        Steps:
            1. Navigate to login page
            2. Check login button state

        Expected: Login button is enabled
        """
        login_page = LoginPage(page)
        await login_page.navigate()

        assert await login_page.is_login_button_enabled(), "Login button should be enabled"

        logger.info("✓ Login button is enabled")

    async def test_error_message_can_be_dismissed(self, page: Page) -> None:
        """
        Test that error messages can be dismissed.

        Steps:
            1. Navigate to login page
            2. Trigger an error (empty credentials)
            3. Click error close button
            4. Verify error message is hidden

        Expected: Error message disappears when closed
        """
        login_page = LoginPage(page)
        await login_page.navigate()

        # Trigger error
        await login_page.click_login_button()
        assert await login_page.is_error_displayed(), "Error should be displayed"

        # Dismiss error
        await login_page.close_error_message()

        # Verify error is gone
        assert not await login_page.is_error_displayed(), "Error should be dismissed"

        logger.info("✓ Error message can be dismissed")

    async def test_credentials_list_displayed(self, page: Page) -> None:
        """
        Test that accepted credentials list is displayed.

        SauceDemo shows accepted usernames on the login page.

        Steps:
            1. Navigate to login page
            2. Retrieve displayed credentials
            3. Verify list is not empty

        Expected: Credentials list is displayed
        """
        login_page = LoginPage(page)
        await login_page.navigate()

        credentials = await login_page.get_login_credentials_list()

        assert len(credentials["usernames"]) > 0, "Should display accepted usernames"
        assert len(credentials["password"]) > 0, "Should display password"

        logger.info(f"✓ Found {len(credentials['usernames'])} accepted usernames")

    async def test_clear_fields_functionality(self, page: Page) -> None:
        """
        Test clearing input fields.

        Steps:
            1. Navigate to login page
            2. Enter credentials
            3. Clear fields
            4. Verify fields are empty

        Expected: Fields can be cleared
        """
        login_page = LoginPage(page)
        await login_page.navigate()

        # Enter credentials
        await login_page.enter_username("test_user")
        await login_page.enter_password("test_password")

        # Clear fields
        await login_page.clear_all_fields()

        # Verify fields are empty
        username = await login_page.get_username_value()
        password = await login_page.get_password_value()

        assert username == "", "Username field should be empty"
        assert password == "", "Password field should be empty"

        logger.info("✓ Fields can be cleared successfully")


@pytest.mark.login
@pytest.mark.regression
class TestLoginEdgeCases:
    """
    Test suite for login edge cases and boundary conditions.
    """

    async def test_login_with_special_characters_in_username(self, page: Page) -> None:
        """
        Test login with special characters in username.

        Steps:
            1. Navigate to login page
            2. Enter username with special characters
            3. Attempt login
            4. Verify appropriate error handling

        Expected: System handles special characters gracefully
        """
        login_page = LoginPage(page)
        await login_page.navigate()

        await login_page.login("user@#$%", settings.standard_password)

        assert await login_page.is_error_displayed(), "Error should be displayed for invalid username"

        logger.info("✓ Special characters in username handled correctly")

    async def test_login_case_sensitivity(self, page: Page) -> None:
        """
        Test that login is case-sensitive.

        Steps:
            1. Navigate to login page
            2. Enter username in different case
            3. Attempt login
            4. Verify login fails

        Expected: Username is case-sensitive
        """
        login_page = LoginPage(page)
        await login_page.navigate()

        # Try uppercase username
        uppercase_username = settings.standard_user.upper()
        await login_page.login(uppercase_username, settings.standard_password)

        assert await login_page.is_error_displayed(), "Login should fail with different case"

        logger.info("✓ Login is case-sensitive")

    async def test_multiple_failed_login_attempts(self, page: Page) -> None:
        """
        Test multiple failed login attempts.

        Steps:
            1. Navigate to login page
            2. Attempt login with wrong credentials 3 times
            3. Verify error message is displayed each time

        Expected: Error is shown for each failed attempt
        """
        login_page = LoginPage(page)
        await login_page.navigate()

        # Attempt multiple failed logins
        for i in range(3):
            await login_page.clear_all_fields()
            await login_page.login("invalid_user", "wrong_password")

            assert await login_page.is_error_displayed(), (
                f"Error should be displayed on attempt {i + 1}"
            )

            if i < 2:  # Don't close on last iteration
                await login_page.close_error_message()

        logger.info("✓ Multiple failed attempts handled correctly")
