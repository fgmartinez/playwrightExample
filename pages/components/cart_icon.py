"""Shopping cart icon component in the top-right header."""

import logging

from playwright.sync_api import Page

from pages.page_helpers import get_text, is_visible_safe

logger = logging.getLogger(__name__)


class CartIcon:
    """Cart link and badge displayed in the page header.

    Present on every authenticated page.  The badge shows the number of
    items currently in the cart and is hidden when the cart is empty.
    """

    def __init__(self, page: Page) -> None:
        self._link = page.locator(".shopping_cart_link")
        self._badge = page.locator(".shopping_cart_badge")

    def click(self) -> None:
        """Navigate to the shopping cart page."""
        logger.info("Navigating to cart")
        self._link.click()

    def get_count(self) -> int:
        """Return the number shown on the badge, or 0 if hidden."""
        if is_visible_safe(self._badge):
            text = get_text(self._badge)
            return int(text) if text else 0
        return 0

    def has_items(self) -> bool:
        """Return True when the badge is visible (cart is non-empty)."""
        return is_visible_safe(self._badge)
