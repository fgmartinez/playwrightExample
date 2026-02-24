"""Cart tests -- display, operations, and navigation."""

import pytest
from playwright.sync_api import Page, expect

from config import UserType
from pages import CartPage, LoginPage, ProductsPage

import logging

logger = logging.getLogger(__name__)


@pytest.mark.cart
@pytest.mark.smoke
class TestCartDisplay:
    """Verify cart page renders items correctly."""

    def test_cart_page_loads(self, cart_with_items: CartPage) -> None:
        """Cart page loads and shows the expected title."""
        assert cart_with_items.is_loaded()
        expect(cart_with_items.title).to_contain_text("Your Cart")

    def test_cart_displays_added_items(self, cart_with_items: CartPage) -> None:
        """The two items added by the fixture are visible with full details."""
        assert cart_with_items.get_item_count() == 2

        names = cart_with_items.get_all_item_names()
        details = cart_with_items.get_item_details(names[0])

        assert details["name"] == names[0]
        assert details["description"]
        assert "$" in details["price"]
        assert details["quantity"] == "1"

    def test_empty_cart(self, page: Page) -> None:
        """An empty cart has zero items."""
        lp = LoginPage(page)
        lp.navigate()
        lp.login_as(UserType.STANDARD)

        pp = ProductsPage(page)
        pp.go_to_cart()

        cp = CartPage(page)
        assert cp.is_empty()


@pytest.mark.cart
@pytest.mark.smoke
class TestCartOperations:
    """Removing items and calculating totals."""

    def test_remove_item(self, cart_with_items: CartPage) -> None:
        """A single item can be removed from the cart."""
        names = cart_with_items.get_all_item_names()
        cart_with_items.remove_item(names[0])

        assert cart_with_items.get_item_count() == 1
        assert not cart_with_items.has_item(names[0])

    def test_cart_total(self, cart_with_items: CartPage) -> None:
        """Cart total equals the sum of individual item prices."""
        prices = cart_with_items.get_all_item_prices()
        assert cart_with_items.get_total() == sum(prices)


@pytest.mark.cart
class TestCartNavigation:
    """Navigation from the cart page."""

    def test_continue_shopping(self, cart_with_items: CartPage) -> None:
        """Continue-shopping button returns to the products page."""
        cart_with_items.continue_shopping()
        assert "/inventory.html" in cart_with_items.current_url

    def test_proceed_to_checkout(self, cart_with_items: CartPage) -> None:
        """Checkout button navigates to the checkout-info page."""
        cart_with_items.proceed_to_checkout()
        assert "/checkout-step-one.html" in cart_with_items.current_url
