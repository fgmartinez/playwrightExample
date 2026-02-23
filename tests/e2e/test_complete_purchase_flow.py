"""
End-to-End Purchase Flow Tests
===============================
Comprehensive end-to-end tests that simulate complete user journeys
through the SauceDemo application.
"""

import pytest
from playwright.async_api import Page, expect

from config import UserType
from pages import (
    CartPage,
    CheckoutCompletePage,
    CheckoutInfoPage,
    CheckoutOverviewPage,
    LoginPage,
    ProductsPage,
)
import logging

from utils.decorators import log_execution_time
from utils.helpers import generate_test_user_data

logger = logging.getLogger(__name__)


@pytest.mark.e2e
@pytest.mark.smoke
class TestCompletePurchaseFlow:
    """End-to-end tests for complete purchase flows."""

    @log_execution_time
    async def test_complete_purchase_single_product(self, page: Page) -> None:
        """Test complete purchase flow with a single product."""
        # Step 1: Login
        login_page = LoginPage(page)
        await login_page.navigate()
        await login_page.login_as(UserType.STANDARD)
        assert await login_page.is_login_successful(), "Login should succeed"
        logger.info("Step 1: Logged in successfully")

        # Step 2: Browse and add product
        products_page = ProductsPage(page)
        await products_page.wait_for_page_load()
        product_names = await products_page.get_all_product_names()
        product_to_buy = product_names[0]

        await products_page.add_to_cart(product_to_buy)
        assert await products_page.get_cart_count() == 1, "Cart should have 1 item"
        logger.info(f"Step 2: Added '{product_to_buy}' to cart")

        # Step 3: Go to cart
        await products_page.go_to_cart()
        cart_page = CartPage(page)
        assert await cart_page.has_item(product_to_buy), (
            f"'{product_to_buy}' should be in cart"
        )
        logger.info("Step 3: Navigated to cart, item present")

        # Step 4: Proceed to checkout
        await cart_page.proceed_to_checkout()
        checkout_info = CheckoutInfoPage(page)
        assert await checkout_info.is_loaded(), "Checkout info page should load"
        logger.info("Step 4: Proceeded to checkout")

        # Step 5: Fill checkout information
        user_data = generate_test_user_data()
        await checkout_info.fill_info(
            user_data["firstName"],
            user_data["lastName"],
            user_data["zipCode"],
        )
        await checkout_info.continue_checkout()
        logger.info("Step 5: Filled checkout information")

        # Step 6: Review and complete order
        overview = CheckoutOverviewPage(page)
        assert await overview.is_loaded(), "Overview page should load"

        order_items = await overview.get_item_names()
        assert product_to_buy in order_items, "Product should be in order"

        assert await overview.verify_total_calculation(), "Total calculation should be correct"
        logger.info("Step 6: Reviewed order, calculations correct")

        # Step 7: Finish checkout
        await overview.finish()

        # Step 8: Verify completion
        complete = CheckoutCompletePage(page)
        assert await complete.is_order_complete(), "Order should be complete"
        await expect(complete.complete_header).to_be_visible()
        await expect(complete.pony_image).to_be_visible()
        logger.info("Step 7-8: Order completed successfully")

    @log_execution_time
    async def test_complete_purchase_multiple_products(self, page: Page) -> None:
        """Test complete purchase flow with multiple products."""
        login_page = LoginPage(page)
        await login_page.navigate()
        await login_page.login_as(UserType.STANDARD)
        logger.info("Logged in")

        products_page = ProductsPage(page)
        product_names = await products_page.get_all_product_names()
        products_to_buy = product_names[:3]

        await products_page.add_multiple_to_cart(products_to_buy)
        assert await products_page.get_cart_count() == 3, "Cart should have 3 items"
        logger.info(f"Added {len(products_to_buy)} products to cart")

        await products_page.go_to_cart()
        cart_page = CartPage(page)
        cart_items = await cart_page.get_all_item_names()
        assert len(cart_items) == 3, "Cart should show 3 items"
        logger.info("Cart contains all products")

        await cart_page.proceed_to_checkout()

        checkout_info = CheckoutInfoPage(page)
        user_data = generate_test_user_data()
        await checkout_info.fill_info(
            user_data["firstName"],
            user_data["lastName"],
            user_data["zipCode"],
        )
        await checkout_info.continue_checkout()

        overview = CheckoutOverviewPage(page)
        order_items = await overview.get_item_names()
        assert len(order_items) == 3, "Order should contain 3 items"
        logger.info("Order contains all products")

        await overview.finish()

        complete = CheckoutCompletePage(page)
        assert await complete.is_order_complete(), "Order should be complete"
        logger.info("Multiple product purchase completed successfully")

    @log_execution_time
    async def test_complete_purchase_with_sorting(self, page: Page) -> None:
        """Test purchase flow with product sorting."""
        login_page = LoginPage(page)
        await login_page.navigate()
        await login_page.login_as(UserType.STANDARD)

        products_page = ProductsPage(page)
        await products_page.sort_by("lohi")
        assert await products_page.verify_sorted_by_price_asc(), (
            "Products should be sorted by price"
        )
        logger.info("Products sorted by price (low to high)")

        product_names = await products_page.get_all_product_names()
        cheapest_product = product_names[0]

        await products_page.add_to_cart(cheapest_product)
        logger.info(f"Added cheapest product: {cheapest_product}")

        await products_page.go_to_cart()

        cart_page = CartPage(page)
        await cart_page.proceed_to_checkout()

        checkout_info = CheckoutInfoPage(page)
        user_data = generate_test_user_data()
        await checkout_info.fill_info(
            user_data["firstName"],
            user_data["lastName"],
            user_data["zipCode"],
        )
        await checkout_info.continue_checkout()

        overview = CheckoutOverviewPage(page)
        await overview.finish()

        complete = CheckoutCompletePage(page)
        assert await complete.is_order_complete(), "Order should be complete"
        logger.info("Purchase with sorting completed successfully")

    @log_execution_time
    async def test_complete_purchase_with_cart_modification(self, page: Page) -> None:
        """Test purchase flow with cart modifications."""
        login_page = LoginPage(page)
        await login_page.navigate()
        await login_page.login_as(UserType.STANDARD)

        products_page = ProductsPage(page)
        product_names = await products_page.get_all_product_names()
        await products_page.add_multiple_to_cart(product_names[:3])
        logger.info("Added 3 products to cart")

        await products_page.go_to_cart()

        cart_page = CartPage(page)
        cart_items = await cart_page.get_all_item_names()
        item_to_remove = cart_items[0]

        await cart_page.remove_item(item_to_remove)
        assert await cart_page.get_item_count() == 2, "Cart should have 2 items"
        logger.info(f"Removed '{item_to_remove}' from cart")

        await cart_page.proceed_to_checkout()

        checkout_info = CheckoutInfoPage(page)
        user_data = generate_test_user_data()
        await checkout_info.fill_info(
            user_data["firstName"],
            user_data["lastName"],
            user_data["zipCode"],
        )
        await checkout_info.continue_checkout()

        overview = CheckoutOverviewPage(page)
        order_items = await overview.get_item_names()
        assert len(order_items) == 2, "Order should contain 2 items"
        assert item_to_remove not in order_items, "Removed item should not be in order"
        logger.info("Order contains only selected items")

        await overview.finish()

        complete = CheckoutCompletePage(page)
        assert await complete.is_order_complete(), "Order should be complete"
        logger.info("Purchase with cart modification completed successfully")

    async def test_full_shopping_experience(self, page: Page) -> None:
        """Test comprehensive shopping experience with all user journey steps."""
        # Step 1: Login
        login_page = LoginPage(page)
        await login_page.navigate()
        await login_page.login_as(UserType.STANDARD)
        logger.info("Step 1: Logged in")

        # Step 2-3: Browse and sort
        products_page = ProductsPage(page)
        initial_count = await products_page.get_product_count()
        assert initial_count > 0, "Should have products"

        await products_page.sort_by("za")
        assert await products_page.verify_sorted_by_name_desc()
        logger.info("Step 2-3: Browsed and sorted products")

        # Step 4: Add items
        product_names = await products_page.get_all_product_names()
        await products_page.add_to_cart(product_names[0])
        logger.info("Step 4: Added item to cart")

        # Step 5: Navigate to cart
        await products_page.go_to_cart()

        # Step 6: Continue shopping
        cart_page = CartPage(page)
        await cart_page.continue_shopping()
        logger.info("Step 5-6: Viewed cart and continued shopping")

        # Step 7: Add more items
        await products_page.add_to_cart(product_names[1])
        assert await products_page.get_cart_count() == 2
        logger.info("Step 7: Added another item")

        # Step 8: Review and checkout
        await products_page.go_to_cart()
        await cart_page.proceed_to_checkout()

        checkout_info = CheckoutInfoPage(page)
        user_data = generate_test_user_data()
        await checkout_info.fill_info(
            user_data["firstName"],
            user_data["lastName"],
            user_data["zipCode"],
        )
        await checkout_info.continue_checkout()

        overview = CheckoutOverviewPage(page)
        await overview.finish()
        logger.info("Step 8: Completed checkout")

        # Step 9: Return to products
        complete = CheckoutCompletePage(page)
        await complete.go_back_to_products()
        assert "/inventory.html" in page.url
        logger.info("Step 9: Returned to products")

        # Step 10: Logout
        products_page = ProductsPage(page)
        await products_page.logout()
        logger.info("Step 10: Logged out")
