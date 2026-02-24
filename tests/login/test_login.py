"""Login tests -- authentication happy-path, failure, and UI basics."""

import pytest
from playwright.sync_api import Page, expect

from config import UserType, settings
from pages import LoginPage

import logging

logger = logging.getLogger(__name__)


@pytest.mark.login
@pytest.mark.smoke
class TestLoginSuccess:
    """Core successful-login scenarios."""

    def test_standard_user_login(self, login_page: LoginPage) -> None:
        """Standard user can log in and land on the inventory page."""
        login_page.login(settings.standard_user, settings.standard_password)

        assert login_page.is_login_successful()
        expect(login_page.page).to_have_url(f"{settings.base_url}/inventory.html")

    @pytest.mark.parametrize("user_type", [UserType.PROBLEM, UserType.PERFORMANCE])
    def test_alternate_user_login(self, page: Page, user_type: UserType) -> None:
        """Problem and performance-glitch users can also log in."""
        lp = LoginPage(page)
        lp.navigate()
        lp.login_as(user_type)
        if user_type == UserType.PERFORMANCE:
            page.wait_for_timeout(2000)
        assert lp.is_login_successful()


@pytest.mark.login
@pytest.mark.smoke
class TestLoginFailure:
    """Login rejection scenarios."""

    def test_locked_out_user(self, login_page: LoginPage) -> None:
        """Locked-out user sees a descriptive error."""
        login_page.login_as(UserType.LOCKED)

        assert login_page.error.is_visible()
        msg = login_page.error.get_message()
        assert "locked out" in msg.lower()

    def test_invalid_credentials(self, login_page: LoginPage) -> None:
        """Invalid username/password combination is rejected."""
        login_page.login("invalid_user", "wrong_password")

        assert login_page.error.is_visible()
        msg = login_page.error.get_message()
        assert "username" in msg.lower() or "password" in msg.lower()

    @pytest.mark.parametrize(
        "username, password, expected_keyword",
        [
            ("", "secret_sauce", "username"),
            ("standard_user", "", "password"),
            ("", "", "username"),
        ],
        ids=["empty-username", "empty-password", "both-empty"],
    )
    def test_empty_field_validation(
        self, login_page: LoginPage, username: str, password: str, expected_keyword: str
    ) -> None:
        """Empty fields trigger a required-field error mentioning the field name."""
        login_page.login(username, password)

        assert login_page.error.is_visible()
        msg = login_page.error.get_message()
        assert expected_keyword in msg.lower()


@pytest.mark.login
class TestLoginUI:
    """Basic UI checks for the login page."""

    def test_page_elements_visible(self, login_page: LoginPage) -> None:
        """All critical login elements are rendered."""
        assert login_page.is_loaded()
        expect(login_page.username_input).to_be_visible()
        expect(login_page.password_input).to_be_visible()
        expect(login_page.login_button).to_be_visible()

    def test_error_can_be_dismissed(self, login_page: LoginPage) -> None:
        """The error banner can be closed after a failed attempt."""
        login_page.click_login_button()
        assert login_page.error.is_visible()

        login_page.error.dismiss()
        assert not login_page.error.is_visible()
