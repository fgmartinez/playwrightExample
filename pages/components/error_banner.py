"""Error banner component reused on login and checkout pages."""

import logging

from playwright.sync_api import Page

from pages.page_helpers import get_text, is_visible_safe

logger = logging.getLogger(__name__)


class ErrorBanner:
    """Dismissible error message banner.

    Appears on the login page and checkout-information page when form
    validation fails.  Provides methods to read the message and dismiss it.
    """

    def __init__(self, page: Page) -> None:
        self._container = page.get_by_test_id("error")
        self._close_button = page.locator(".error-button")

    def is_visible(self) -> bool:
        """Check whether the error banner is currently displayed."""
        return is_visible_safe(self._container)

    def get_message(self) -> str:
        """Return the error message text, or an empty string if hidden."""
        if self.is_visible():
            return get_text(self._container)
        return ""

    def dismiss(self) -> None:
        """Close the error banner if it is visible."""
        if self.is_visible():
            self._close_button.click()
