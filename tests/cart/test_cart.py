"""
Shopping Cart Tests
===================
Test cases for shopping cart functionality including viewing, removing,
calculations, and navigation.
"""

import pytest
from playwright.async_api import Page

import logging

from pages import CartPage, LoginPage, ProductsPage

logger = logging.getLogger(__name__)


@pytest.fixture
async def cart_with_items(page: Page) -> CartPage:
    """Fixture providing cart page with items already added."""
    login_page = LoginPage(page)
    await login_page.navigate()
    await login_page.login_as_standard_user()

    products_page = ProductsPage(page)
    await products_page.wait_for_page_load()

    product_names = await products_page.get_all_product_names()
    await products_page.add_multiple_to_cart(product_names[:2])

    await products_page.go_to_cart()

    cart_page = CartPage(page)
    await cart_page.wait_for_page_load()
    return cart_page


@pytest.mark.cart
@pytest.mark.smoke
class TestCartDisplay:
    """Tests for cart page display and information."""

    async def test_cart_page_loads(self, cart_with_items: CartPage) -> None:
        """Verify cart page loads successfully."""
        cart_page = cart_with_items

        assert await cart_page.is_loaded(), "Cart page should load"
        await cart_page.assert_displayed()
        logger.info("Cart page loaded successfully")

    async def test_cart_displays_added_items(self, cart_with_items: CartPage) -> None:
        """Verify cart displays all added items."""
        cart_page = cart_with_items

        item_count = await cart_page.get_item_count()
        assert item_count == 2, f"Cart should contain 2 items, got: {item_count}"

        item_names = await cart_page.get_all_item_names()
        assert len(item_names) == 2, "Should display 2 item names"
        logger.info(f"Cart displays {item_count} items correctly")

    async def test_cart_item_details(self, cart_with_items: CartPage) -> None:
        """Verify cart item details are complete."""
        cart_page = cart_with_items

        item_names = await cart_page.get_all_item_names()
        first_item = item_names[0]

        details = await cart_page.get_item_details(first_item)

        assert details["name"] == first_item
        assert len(details["description"]) > 0, "Should have description"
        assert "$" in details["price"], "Should have price"
        assert details["quantity"] == "1", "Default quantity should be 1"
        logger.info(f"Item details complete for '{first_item}'")

    async def test_empty_cart_display(self, page: Page) -> None:
        """Verify empty cart display."""
        login_page = LoginPage(page)
        await login_page.navigate()
        await login_page.login_as_standard_user()

        products_page = ProductsPage(page)
        await products_page.go_to_cart()

        cart_page = CartPage(page)
        assert await cart_page.is_empty(), "Cart should be empty"
        logger.info("Empty cart displayed correctly")


@pytest.mark.cart
@pytest.mark.smoke
class TestCartOperations:
    """Tests for cart operations like removing items."""

    async def test_remove_single_item(self, cart_with_items: CartPage) -> None:
        """Verify single item can be removed from cart."""
        cart_page = cart_with_items

        initial_count = await cart_page.get_item_count()
        item_names = await cart_page.get_all_item_names()
        item_to_remove = item_names[0]

        await cart_page.remove_item(item_to_remove)

        new_count = await cart_page.get_item_count()
        assert new_count == initial_count - 1, "Item count should decrease by 1"

        assert not await cart_page.has_item(item_to_remove), (
            f"Item '{item_to_remove}' should not be in cart"
        )
        logger.info(f"Successfully removed '{item_to_remove}' from cart")

    async def test_remove_all_items(self, cart_with_items: CartPage) -> None:
        """Verify all items can be removed from cart."""
        cart_page = cart_with_items

        await cart_page.remove_all_items()

        assert await cart_page.is_empty(), "Cart should be empty"
        logger.info("Successfully removed all items from cart")

    async def test_calculate_cart_total(self, cart_with_items: CartPage) -> None:
        """Verify cart total calculation."""
        cart_page = cart_with_items

        prices = await cart_page.get_all_item_prices()
        expected_total = sum(prices)

        calculated_total = await cart_page.get_total()

        assert calculated_total == expected_total, (
            f"Total should be {expected_total}, got: {calculated_total}"
        )
        logger.info(f"Cart total calculated correctly: ${calculated_total:.2f}")


@pytest.mark.cart
class TestCartNavigation:
    """Tests for navigation from cart page."""

    async def test_continue_shopping(self, cart_with_items: CartPage) -> None:
        """Verify continue shopping button returns to products."""
        cart_page = cart_with_items

        await cart_page.continue_shopping()

        assert "/inventory.html" in cart_page.current_url, (
            "Should return to products page"
        )
        logger.info("Successfully returned to products page")

    async def test_proceed_to_checkout(self, cart_with_items: CartPage) -> None:
        """Verify proceed to checkout navigation."""
        cart_page = cart_with_items

        await cart_page.proceed_to_checkout()

        assert "/checkout-step-one.html" in cart_page.current_url, (
            "Should navigate to checkout"
        )
        logger.info("Successfully proceeded to checkout")
