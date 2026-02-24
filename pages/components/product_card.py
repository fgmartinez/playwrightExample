"""Product card component on the inventory page."""

import logging

from playwright.sync_api import Locator, Page

logger = logging.getLogger(__name__)


class ProductCard:
    """A single product card on the inventory page.

    Encapsulates the product's name, description, price, image, and the
    add-to-cart / remove buttons.  Use the class methods to obtain cards
    from the page.
    """

    NAME = ".inventory_item_name"
    DESCRIPTION = ".inventory_item_desc"
    PRICE = ".inventory_item_price"
    IMAGE = ".inventory_item_img"
    ADD_TO_CART = "button[id^='add-to-cart']"
    REMOVE = "button[id^='remove']"

    def __init__(self, root: Locator) -> None:
        self.root = root
        self.name = root.locator(self.NAME)
        self.description = root.locator(self.DESCRIPTION)
        self.price = root.locator(self.PRICE)
        self.image = root.locator(self.IMAGE)
        self.add_to_cart_button = root.locator(self.ADD_TO_CART)
        self.remove_button = root.locator(self.REMOVE)

    # -- Factory helpers -----------------------------------------------------

    @classmethod
    def all_cards(cls, page: Page) -> Locator:
        """Return a locator matching every product card on the page."""
        return page.locator(".inventory_item")

    @classmethod
    def by_name(cls, page: Page, name: str) -> "ProductCard":
        """Return the product card whose text contains *name*."""
        root = cls.all_cards(page).filter(has_text=name).first
        return cls(root)

    # -- Data access ---------------------------------------------------------

    def get_name(self) -> str:
        text = self.name.text_content()
        return (text or "").strip()

    def get_description(self) -> str:
        text = self.description.text_content()
        return (text or "").strip()

    def get_price(self) -> float:
        text = self.price.text_content()
        if text:
            return float(text.strip().replace("$", ""))
        return 0.0

    def get_details(self) -> dict[str, str]:
        return {
            "name": self.get_name(),
            "description": self.get_description(),
            "price": (self.price.text_content() or "").strip(),
        }

    # -- Cart actions --------------------------------------------------------

    def add_to_cart(self) -> None:
        logger.debug(f"Adding to cart: {self.get_name()}")
        self.add_to_cart_button.click()

    def remove_from_cart(self) -> None:
        logger.debug(f"Removing from cart: {self.get_name()}")
        self.remove_button.click()

    def is_in_cart(self) -> bool:
        """True when the remove button is visible (item already in cart)."""
        return self.remove_button.is_visible()

    def click_name(self) -> None:
        """Click the product name to navigate to its detail page."""
        self.name.click()
