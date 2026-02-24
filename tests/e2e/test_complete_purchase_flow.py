"""End-to-end purchase-flow tests.

Each test simulates a full user journey from login to order confirmation.
"""

import pytest
from playwright.sync_api import Page, expect

from config import UserType
from pages import (
    CartPage,
    CheckoutCompletePage,
    CheckoutInfoPage,
    CheckoutOverviewPage,
    LoginPage,
    ProductsPage,
)
from utils.helpers import generate_test_user_data

import logging

logger = logging.getLogger(__name__)


@pytest.mark.e2e
@pytest.mark.smoke
class TestCompletePurchaseFlow:

    def test_single_product_purchase(self, page: Page) -> None:
        """Buy one product: login -> add -> cart -> checkout -> confirm."""
        # Login
        login_page = LoginPage(page)
        login_page.navigate()
        login_page.login_as(UserType.STANDARD)
        assert login_page.is_login_successful()
        logger.info("Logged in")

        # Add product
        products = ProductsPage(page)
        products.wait_for_page_load()
        names = products.get_all_product_names()
        products.add_to_cart(names[0])
        assert products.get_cart_count() == 1
        logger.info(f"Added '{names[0]}' to cart")

        # Cart
        products.go_to_cart()
        cart = CartPage(page)
        assert cart.has_item(names[0])
        logger.info("Item verified in cart")

        # Checkout info
        cart.proceed_to_checkout()
        info = CheckoutInfoPage(page)
        user_data = generate_test_user_data()
        info.fill_info(user_data["firstName"], user_data["lastName"], user_data["zipCode"])
        info.continue_checkout()
        logger.info("Filled checkout info")

        # Overview
        overview = CheckoutOverviewPage(page)
        assert overview.is_loaded()
        assert names[0] in overview.get_item_names()
        assert overview.verify_total_calculation()
        overview.finish()
        logger.info("Order placed")

        # Confirmation
        complete = CheckoutCompletePage(page)
        assert complete.is_order_complete()
        expect(complete.complete_header).to_be_visible()
        logger.info("Purchase completed successfully")

    def test_purchase_with_cart_modification(self, page: Page) -> None:
        """Add three products, remove one, then complete the purchase."""
        login_page = LoginPage(page)
        login_page.navigate()
        login_page.login_as(UserType.STANDARD)
        logger.info("Logged in")

        products = ProductsPage(page)
        names = products.get_all_product_names()
        products.add_multiple_to_cart(names[:3])
        logger.info("Added 3 products")

        products.go_to_cart()
        cart = CartPage(page)
        removed = cart.get_all_item_names()[0]
        cart.remove_item(removed)
        assert cart.get_item_count() == 2
        logger.info(f"Removed '{removed}'")

        cart.proceed_to_checkout()
        info = CheckoutInfoPage(page)
        user_data = generate_test_user_data()
        info.fill_info(user_data["firstName"], user_data["lastName"], user_data["zipCode"])
        info.continue_checkout()

        overview = CheckoutOverviewPage(page)
        order_items = overview.get_item_names()
        assert len(order_items) == 2
        assert removed not in order_items
        overview.finish()

        complete = CheckoutCompletePage(page)
        assert complete.is_order_complete()
        logger.info("Modified-cart purchase completed successfully")
