"""
Cart Page Object
================
Page object for SauceDemo shopping cart page.
Uses CartItem component for individual item interactions.
"""

from playwright.async_api import Page

from pages.base_page import BasePage
from pages.components import CartItem
from utils.logger import get_logger

logger = get_logger(__name__)


class CartPage(BasePage):
    """Page object for the SauceDemo shopping cart page."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.url = "/cart.html"

        # Page elements
        self.title = page.locator(".title")
        self.checkout_button = page.get_by_test_id("checkout")
        self.continue_shopping_button = page.get_by_test_id("continue-shopping")

        # Cart items - use component class
        self._cart_items = CartItem.all_items(page)

    # ========================================================================
    # Cart Item Access
    # ========================================================================

    def item(self, name: str) -> CartItem:
        """Get a CartItem component by item name."""
        return CartItem.by_name(self.page, name)

    async def get_all_items(self) -> list[CartItem]:
        """Get all CartItem components in the cart."""
        items = await self._cart_items.all()
        return [CartItem(item) for item in items]

    async def get_item_count(self) -> int:
        """Get number of items in cart."""
        return await self._cart_items.count()

    async def get_all_item_names(self) -> list[str]:
        """Get names of all items in cart."""
        items = await self.get_all_items()
        return [await item.get_name() for item in items]

    async def get_all_item_prices(self) -> list[float]:
        """Get prices of all items in cart."""
        items = await self.get_all_items()
        return [await item.get_price() for item in items]

    async def get_total(self) -> float:
        """Calculate total of all items."""
        prices = await self.get_all_item_prices()
        return sum(prices)

    async def get_item_details(self, item_name: str) -> dict[str, str]:
        """Get details of a specific cart item by name."""
        return await self.item(item_name).get_details()

    # ========================================================================
    # Cart Operations
    # ========================================================================

    async def remove_item(self, item_name: str) -> None:
        """Remove an item from cart by name."""
        logger.info(f"Removing from cart: {item_name}")
        await self.item(item_name).remove()

    async def remove_all_items(self) -> None:
        """Remove all items from cart."""
        logger.info("Removing all items from cart")
        items = await self.get_all_items()
        for item in items:
            await item.remove()

    async def is_empty(self) -> bool:
        """Check if cart is empty."""
        return await self.get_item_count() == 0

    async def has_item(self, item_name: str) -> bool:
        """Check if item is in cart."""
        names = await self.get_all_item_names()
        return item_name in names

    # ========================================================================
    # Navigation
    # ========================================================================

    async def proceed_to_checkout(self) -> None:
        """Click checkout button."""
        logger.info("Proceeding to checkout")
        await self.checkout_button.click()

    async def continue_shopping(self) -> None:
        """Return to products page."""
        logger.info("Continuing shopping")
        await self.continue_shopping_button.click()

    # ========================================================================
    # Page State
    # ========================================================================

    async def is_loaded(self) -> bool:
        """Check if cart page is loaded."""
        try:
            await self.title.wait_for(state="visible", timeout=5000)
            await self.checkout_button.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False

    # ========================================================================
    # Assertions
    # ========================================================================

    async def assert_displayed(self) -> None:
        """Assert cart page is displayed."""
        await self.assert_visible(self.title)
        await self.assert_has_text(self.title, "Your Cart")

    async def assert_item_count(self, expected: int) -> None:
        """Assert cart has expected number of items."""
        actual = await self.get_item_count()
        assert actual == expected, f"Expected {expected} items, got {actual}"

    async def assert_has_item(self, item_name: str) -> None:
        """Assert item is in cart."""
        assert await self.has_item(item_name), f"Item '{item_name}' should be in cart"

    async def assert_empty(self) -> None:
        """Assert cart is empty."""
        assert await self.is_empty(), "Cart should be empty"
