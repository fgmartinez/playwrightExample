"""Cart line-item component used on the cart and checkout-overview pages."""

import logging

from playwright.sync_api import Locator, Page

logger = logging.getLogger(__name__)


class CartItem:
    """A single line item inside the shopping cart or checkout overview.

    Includes quantity information that is not present on product cards.
    """

    NAME = ".inventory_item_name"
    DESCRIPTION = ".inventory_item_desc"
    PRICE = ".inventory_item_price"
    QUANTITY = ".cart_quantity"
    REMOVE = "button[id^='remove']"

    def __init__(self, root: Locator) -> None:
        self.root = root
        self.name = root.locator(self.NAME)
        self.description = root.locator(self.DESCRIPTION)
        self.price = root.locator(self.PRICE)
        self.quantity = root.locator(self.QUANTITY)
        self.remove_button = root.locator(self.REMOVE)

    # -- Factory helpers -----------------------------------------------------

    @classmethod
    def all_items(cls, page: Page) -> Locator:
        """Return a locator matching every cart item on the page."""
        return page.locator(".cart_item")

    @classmethod
    def by_name(cls, page: Page, name: str) -> "CartItem":
        """Return the cart item whose text contains *name*."""
        root = cls.all_items(page).filter(has_text=name).first
        return cls(root)

    # -- Data access ---------------------------------------------------------

    def get_name(self) -> str:
        text = self.name.text_content()
        return (text or "").strip()

    def get_price(self) -> float:
        text = self.price.text_content()
        if text:
            return float(text.strip().replace("$", ""))
        return 0.0

    def get_quantity(self) -> int:
        text = self.quantity.text_content()
        return int(text.strip()) if text else 0

    def get_details(self) -> dict[str, str]:
        return {
            "name": self.get_name(),
            "description": (self.description.text_content() or "").strip(),
            "price": (self.price.text_content() or "").strip(),
            "quantity": (self.quantity.text_content() or "").strip(),
        }

    # -- Actions -------------------------------------------------------------

    def remove(self) -> None:
        logger.debug(f"Removing from cart: {self.get_name()}")
        self.remove_button.click()
