"""Products page object -- inventory browsing, sorting, and cart actions."""

import logging

from playwright.sync_api import Page

from pages.base_page import AuthenticatedPage
from pages.components.product_card import ProductCard

logger = logging.getLogger(__name__)


class ProductsPage(AuthenticatedPage):
    """Inventory page where the user browses and adds products to the cart.

    Cart-icon, cart-badge and burger-menu concerns are inherited from
    ``AuthenticatedPage`` so this class only owns product-specific logic:
    listing, sorting, and per-product cart operations.
    """

    URL = "/inventory.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.sort_dropdown = page.get_by_test_id("product_sort_container")
        self._product_cards = ProductCard.all_cards(page)

    # -- Product access ------------------------------------------------------

    def product(self, name: str) -> ProductCard:
        """Return a ``ProductCard`` component by product name."""
        return ProductCard.by_name(self.page, name)

    def get_all_products(self) -> list[ProductCard]:
        """Return every ``ProductCard`` on the page."""
        cards = self._product_cards.all()
        return [ProductCard(card) for card in cards]

    def get_product_count(self) -> int:
        return self._product_cards.count()

    def get_all_product_names(self) -> list[str]:
        return [p.get_name() for p in self.get_all_products()]

    def get_all_product_prices(self) -> list[float]:
        return [p.get_price() for p in self.get_all_products()]

    def get_product_details(self, product_name: str) -> dict[str, str]:
        return self.product(product_name).get_details()

    # -- Cart operations (product-level) -------------------------------------

    def add_to_cart(self, product_name: str) -> None:
        logger.info(f"Adding to cart: {product_name}")
        self.product(product_name).add_to_cart()

    def remove_from_cart(self, product_name: str) -> None:
        logger.info(f"Removing from cart: {product_name}")
        self.product(product_name).remove_from_cart()

    def add_multiple_to_cart(self, product_names: list[str]) -> None:
        for name in product_names:
            self.add_to_cart(name)

    def add_all_to_cart(self) -> None:
        for product in self.get_all_products():
            product.add_to_cart()

    def is_product_in_cart(self, product_name: str) -> bool:
        return self.product(product_name).is_in_cart()

    # -- Sorting -------------------------------------------------------------

    def sort_by(self, option: str) -> None:
        """Sort products.  *option* is one of ``az``, ``za``, ``lohi``, ``hilo``."""
        logger.info(f"Sorting by: {option}")
        self.sort_dropdown.select_option(option)

    def get_current_sort(self) -> str:
        return self.sort_dropdown.input_value()

    def is_sorted(self, option: str) -> bool:
        """Verify the product list is ordered according to *option*."""
        if option in ("az", "za"):
            names = self.get_all_product_names()
            return names == sorted(names, reverse=(option == "za"))
        prices = self.get_all_product_prices()
        return prices == sorted(prices, reverse=(option == "hilo"))

    # -- Page state ----------------------------------------------------------

    def is_loaded(self) -> bool:
        try:
            self.title.wait_for(state="visible", timeout=5000)
            self._product_cards.first.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False
