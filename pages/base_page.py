"""Base page classes that form the page-object hierarchy.

``BasePage``
    Minimal base for *all* pages (including the unauthenticated login page).
    Provides navigation, URL access, and the ``is_loaded`` contract.

``AuthenticatedPage``
    Extends ``BasePage`` for pages that require a logged-in session.
    Composes the shared header components (burger menu, cart icon) so that
    every authenticated page gets them automatically without duplicating
    locators or logic.
"""

import logging

from playwright.sync_api import Page

from pages.components.burger_menu import BurgerMenu
from pages.components.cart_icon import CartIcon
from pages.page_helpers import navigate_to, wait_for_load

logger = logging.getLogger(__name__)


class BasePage:
    """Base for all page objects.

    Subclasses must define a ``URL`` class attribute and implement
    ``is_loaded``.
    """

    URL: str = "/"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.title = page.locator(".title")

    @property
    def current_url(self) -> str:
        """The browser's current URL."""
        return self.page.url

    def navigate(self) -> None:
        """Navigate to this page's ``URL``."""
        navigate_to(self.page, self.URL)

    def wait_for_page_load(self) -> None:
        """Wait until the page reaches *networkidle*."""
        wait_for_load(self.page)

    def is_loaded(self) -> bool:
        """Return ``True`` when the page is fully loaded.

        Subclasses should override this with page-specific checks.
        """
        raise NotImplementedError


class AuthenticatedPage(BasePage):
    """Base for pages that require an authenticated session.

    Composes the ``BurgerMenu`` and ``CartIcon`` components that are present
    in the header of every post-login page, following the Single
    Responsibility Principle: the menu and cart logic live in their own
    components, not in every page that happens to display them.
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.burger_menu = BurgerMenu(page)
        self.cart_icon = CartIcon(page)

    # -- Convenience delegates (thin wrappers keep test code concise) --------

    def go_to_cart(self) -> None:
        """Navigate to the shopping cart page."""
        self.cart_icon.click()

    def get_cart_count(self) -> int:
        """Return the number of items shown on the cart badge."""
        return self.cart_icon.get_count()

    def has_cart_items(self) -> bool:
        """Return ``True`` when the cart contains at least one item."""
        return self.cart_icon.has_items()

    def logout(self) -> None:
        """Log out via the burger-menu sidebar."""
        self.burger_menu.logout()
