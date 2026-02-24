"""Login page object -- authentication entry point."""

import logging

from playwright.sync_api import Page

from config import UserType, settings
from pages.base_page import BasePage
from pages.components.error_banner import ErrorBanner
from pages.page_helpers import get_text

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """Login page -- the only *unauthenticated* page in the application.

    Extends ``BasePage`` (not ``AuthenticatedPage``) because there is no
    burger menu or cart icon before the user logs in.  Error-handling is
    delegated to the ``ErrorBanner`` component shared with the checkout page.
    """

    URL = "/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.username_input = page.get_by_test_id("username")
        self.password_input = page.get_by_test_id("password")
        self.login_button = page.get_by_test_id("login-button")
        self.error = ErrorBanner(page)
        self.credentials_panel = page.locator("#login_credentials")
        self.password_panel = page.locator(".login_password")

    # -- Actions -------------------------------------------------------------

    def login(self, username: str, password: str) -> None:
        logger.info(f"Logging in as: {username}")
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

    def login_as(self, user_type: UserType) -> None:
        username, password = settings.users[user_type]
        self.login(username, password)

    def enter_username(self, username: str) -> None:
        self.username_input.fill(username)

    def enter_password(self, password: str) -> None:
        self.password_input.fill(password)

    def click_login_button(self) -> None:
        self.login_button.click()

    def clear_form(self) -> None:
        self.username_input.clear()
        self.password_input.clear()

    # -- State checks --------------------------------------------------------

    def is_login_successful(self) -> bool:
        try:
            self.page.wait_for_url("**/inventory.html", timeout=5000)
            logger.info("Login successful")
            return True
        except Exception:
            logger.warning("Login failed or timed out")
            return False

    def get_username_value(self) -> str:
        return self.username_input.input_value()

    def get_password_value(self) -> str:
        return self.password_input.input_value()

    def is_login_button_enabled(self) -> bool:
        return self.login_button.is_enabled()

    def get_login_credentials_list(self) -> dict[str, list[str] | str]:
        usernames_text = get_text(self.credentials_panel)
        password_text = get_text(self.password_panel)
        lines = [line.strip() for line in usernames_text.split("\n") if line.strip()]
        usernames = lines[1:] if len(lines) > 1 else lines
        pw_lines = [line.strip() for line in password_text.split("\n") if line.strip()]
        password = pw_lines[-1] if pw_lines else ""
        return {"usernames": usernames, "password": password}

    def is_loaded(self) -> bool:
        try:
            self.username_input.wait_for(state="visible", timeout=5000)
            self.login_button.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False
