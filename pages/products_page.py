"""
Products Page Object
====================
Page object for SauceDemo inventory/products page.
Uses ProductCard component for individual product interactions.
"""

from playwright.async_api import Page, expect

import logging

from pages.components import ProductCard
from pages.page_helpers import BasePage, get_text, is_visible_safe

logger = logging.getLogger(__name__)


class ProductsPage(BasePage):
    """Page object for the SauceDemo products/inventory page."""

    URL = "/inventory.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        # Header elements
        self.title = page.locator(".title")
        self.cart_link = page.locator(".shopping_cart_link")
        self.cart_badge = page.locator(".shopping_cart_badge")

        # Sort dropdown
        self.sort_dropdown = page.get_by_test_id("product_sort_container")

        # Menu
        self.menu_button = page.locator("#react-burger-menu-btn")
        self.menu_close_button = page.locator("#react-burger-cross-btn")
        self.logout_link = page.locator("#logout_sidebar_link")

        # Product cards - use component class
        self._product_cards = ProductCard.all_cards(page)

    # ========================================================================
    # Product Card Access
    # ========================================================================

    def product(self, name: str) -> ProductCard:
        """Get a ProductCard component by product name."""
        return ProductCard.by_name(self.page, name)

    async def get_all_products(self) -> list[ProductCard]:
        """Get all ProductCard components on the page."""
        cards = await self._product_cards.all()
        return [ProductCard(card) for card in cards]

    async def get_product_count(self) -> int:
        """Get count of products displayed."""
        return await self._product_cards.count()

    async def get_all_product_names(self) -> list[str]:
        """Get names of all products."""
        products = await self.get_all_products()
        return [await p.get_name() for p in products]

    async def get_all_product_prices(self) -> list[float]:
        """Get prices of all products."""
        products = await self.get_all_products()
        return [await p.get_price() for p in products]

    async def get_product_details(self, product_name: str) -> dict[str, str]:
        """Get details of a specific product by name."""
        return await self.product(product_name).get_details()

    # ========================================================================
    # Cart Operations
    # ========================================================================

    async def add_to_cart(self, product_name: str) -> None:
        """Add a product to cart by name."""
        logger.info(f"Adding to cart: {product_name}")
        await self.product(product_name).add_to_cart()

    async def remove_from_cart(self, product_name: str) -> None:
        """Remove a product from cart by name."""
        logger.info(f"Removing from cart: {product_name}")
        await self.product(product_name).remove_from_cart()

    async def add_multiple_to_cart(self, product_names: list[str]) -> None:
        """Add multiple products to cart."""
        for name in product_names:
            await self.add_to_cart(name)

    async def add_all_to_cart(self) -> None:
        """Add all products to cart."""
        products = await self.get_all_products()
        for product in products:
            await product.add_to_cart()

    async def is_product_in_cart(self, product_name: str) -> bool:
        """Check if a product is in cart."""
        return await self.product(product_name).is_in_cart()

    # ========================================================================
    # Cart Badge
    # ========================================================================

    async def get_cart_count(self) -> int:
        """Get number of items shown in cart badge (0 if not visible)."""
        if await is_visible_safe(self.cart_badge):
            text = await get_text(self.cart_badge)
            return int(text) if text else 0
        return 0

    async def has_cart_badge(self) -> bool:
        """Check if cart badge is visible (has items)."""
        return await is_visible_safe(self.cart_badge)

    # ========================================================================
    # Navigation
    # ========================================================================

    async def go_to_cart(self) -> None:
        """Navigate to shopping cart."""
        logger.info("Navigating to cart")
        await self.cart_link.click()

    async def open_menu(self) -> None:
        """Open the hamburger menu."""
        await self.menu_button.click()
        await self.logout_link.wait_for(state="visible")

    async def logout(self) -> None:
        """Logout via menu."""
        logger.info("Logging out")
        await self.open_menu()
        await self.logout_link.click()

    # ========================================================================
    # Sorting
    # ========================================================================

    async def sort_by(self, option: str) -> None:
        """
        Sort products.

        Args:
            option: Sort value - "az", "za", "lohi", "hilo"
        """
        logger.info(f"Sorting by: {option}")
        await self.sort_dropdown.select_option(option)

    async def get_current_sort(self) -> str:
        """Get currently selected sort option."""
        return await self.sort_dropdown.input_value()

    async def verify_sorted_by_name_asc(self) -> bool:
        """Verify products are sorted A-Z."""
        names = await self.get_all_product_names()
        return names == sorted(names)

    async def verify_sorted_by_name_desc(self) -> bool:
        """Verify products are sorted Z-A."""
        names = await self.get_all_product_names()
        return names == sorted(names, reverse=True)

    async def verify_sorted_by_price_asc(self) -> bool:
        """Verify products are sorted by price low to high."""
        prices = await self.get_all_product_prices()
        return prices == sorted(prices)

    async def verify_sorted_by_price_desc(self) -> bool:
        """Verify products are sorted by price high to low."""
        prices = await self.get_all_product_prices()
        return prices == sorted(prices, reverse=True)

    # ========================================================================
    # Page State
    # ========================================================================

    async def is_loaded(self) -> bool:
        """Check if page is fully loaded."""
        try:
            await self.title.wait_for(state="visible", timeout=5000)
            await self._product_cards.first.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False

    # ========================================================================
    # Assertions
    # ========================================================================

    async def assert_displayed(self) -> None:
        """Assert products page is displayed."""
        await expect(self.title).to_be_visible()
        await expect(self.title).to_contain_text("Products")

    async def assert_cart_count(self, expected: int) -> None:
        """Assert cart badge shows expected count."""
        actual = await self.get_cart_count()
        assert actual == expected, f"Expected cart count {expected}, got {actual}"

    async def assert_product_in_cart(self, product_name: str) -> None:
        """Assert product is in cart."""
        assert await self.is_product_in_cart(product_name), \
            f"Product '{product_name}' should be in cart"
