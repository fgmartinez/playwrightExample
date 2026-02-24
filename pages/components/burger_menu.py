"""Burger menu sidebar component shared across all authenticated pages."""

import logging

from playwright.sync_api import Page

logger = logging.getLogger(__name__)


class BurgerMenu:
    """Sidebar navigation menu accessible from every authenticated page.

    Encapsulates the hamburger button, sidebar links (All Items, About,
    Logout, Reset App State), and the close button.
    """

    def __init__(self, page: Page) -> None:
        self._open_button = page.locator("#react-burger-menu-btn")
        self._close_button = page.locator("#react-burger-cross-btn")
        self._logout_link = page.locator("#logout_sidebar_link")
        self._all_items_link = page.locator("#inventory_sidebar_link")
        self._about_link = page.locator("#about_sidebar_link")
        self._reset_link = page.locator("#reset_sidebar_link")

    def open(self) -> None:
        """Open the sidebar menu and wait for it to become interactive."""
        self._open_button.click()
        self._logout_link.wait_for(state="visible")

    def close(self) -> None:
        """Close the sidebar menu."""
        self._close_button.click()

    def logout(self) -> None:
        """Log out via the sidebar menu."""
        logger.info("Logging out via burger menu")
        self.open()
        self._logout_link.click()

    def go_to_all_items(self) -> None:
        """Navigate to the inventory page via the sidebar."""
        self.open()
        self._all_items_link.click()

    def reset_app_state(self) -> None:
        """Reset the application state via the sidebar."""
        self.open()
        self._reset_link.click()
