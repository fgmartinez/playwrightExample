"""Cart page object -- view, modify, and check out the shopping cart."""

import logging

from playwright.sync_api import Page

from pages.base_page import AuthenticatedPage
from pages.components.cart_item import CartItem

logger = logging.getLogger(__name__)


class CartPage(AuthenticatedPage):
    """Shopping-cart page.

    Inherits header components (burger menu, cart icon) from
    ``AuthenticatedPage`` and adds cart-specific actions: item listing,
    removal, totalling, and navigation to checkout.
    """

    URL = "/cart.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.checkout_button = page.get_by_test_id("checkout")
        self.continue_shopping_button = page.get_by_test_id("continue-shopping")
        self._cart_items = CartItem.all_items(page)

    # -- Item access ---------------------------------------------------------

    def item(self, name: str) -> CartItem:
        return CartItem.by_name(self.page, name)

    def get_all_items(self) -> list[CartItem]:
        items = self._cart_items.all()
        return [CartItem(item) for item in items]

    def get_item_count(self) -> int:
        return self._cart_items.count()

    def get_all_item_names(self) -> list[str]:
        return [item.get_name() for item in self.get_all_items()]

    def get_all_item_prices(self) -> list[float]:
        return [item.get_price() for item in self.get_all_items()]

    def get_total(self) -> float:
        return sum(self.get_all_item_prices())

    def get_item_details(self, item_name: str) -> dict[str, str]:
        return self.item(item_name).get_details()

    # -- Cart operations -----------------------------------------------------

    def remove_item(self, item_name: str) -> None:
        logger.info(f"Removing from cart: {item_name}")
        self.item(item_name).remove()

    def remove_all_items(self) -> None:
        logger.info("Removing all items from cart")
        for item in self.get_all_items():
            item.remove()

    def is_empty(self) -> bool:
        return self.get_item_count() == 0

    def has_item(self, item_name: str) -> bool:
        return item_name in self.get_all_item_names()

    # -- Navigation ----------------------------------------------------------

    def proceed_to_checkout(self) -> None:
        logger.info("Proceeding to checkout")
        self.checkout_button.click()

    def continue_shopping(self) -> None:
        logger.info("Continuing shopping")
        self.continue_shopping_button.click()

    # -- Page state ----------------------------------------------------------

    def is_loaded(self) -> bool:
        try:
            self.title.wait_for(state="visible", timeout=5000)
            self.checkout_button.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False
