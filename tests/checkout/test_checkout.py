"""
Checkout Tests
==============
Test cases for the complete checkout flow including customer information,
order review, and order completion.
"""

import pytest
from playwright.async_api import Page

from pages import (
    CartPage,
    CheckoutCompletePage,
    CheckoutInfoPage,
    CheckoutOverviewPage,
    LoginPage,
    ProductsPage,
)
from utils.helpers import generate_test_user_data
from utils.logger import get_logger

logger = get_logger(__name__)


@pytest.fixture
async def checkout_info_page(page: Page) -> CheckoutInfoPage:
    """Fixture providing checkout information page with items in cart."""
    login_page = LoginPage(page)
    await login_page.navigate()
    await login_page.login_as_standard_user()

    products_page = ProductsPage(page)
    product_names = await products_page.get_all_product_names()
    await products_page.add_multiple_to_cart(product_names[:2])
    await products_page.go_to_cart()

    cart_page = CartPage(page)
    await cart_page.proceed_to_checkout()

    return CheckoutInfoPage(page)


@pytest.mark.checkout
@pytest.mark.smoke
class TestCheckoutInformation:
    """Tests for checkout information step."""

    async def test_checkout_info_page_loads(
        self, checkout_info_page: CheckoutInfoPage
    ) -> None:
        """Verify checkout information page loads."""
        checkout_page = checkout_info_page

        assert await checkout_page.is_loaded(), "Checkout info page should load"
        await checkout_page.assert_displayed()
        logger.info("Checkout information page loaded")

    async def test_fill_valid_information(
        self, checkout_info_page: CheckoutInfoPage
    ) -> None:
        """Verify valid information can be filled and submitted."""
        checkout_page = checkout_info_page

        user_data = generate_test_user_data()
        await checkout_page.fill_info(
            user_data["firstName"],
            user_data["lastName"],
            user_data["zipCode"],
        )

        await checkout_page.continue_checkout()

        assert "/checkout-step-two.html" in checkout_page.current_url
        logger.info("Valid information accepted")

    async def test_empty_first_name_validation(
        self, checkout_info_page: CheckoutInfoPage
    ) -> None:
        """Verify validation for empty first name."""
        checkout_page = checkout_info_page

        await checkout_page.fill_info("", "Doe", "12345")
        await checkout_page.continue_checkout()

        assert await checkout_page.has_error(), "Error should be displayed"
        error_message = await checkout_page.get_error_message()
        assert "first name" in error_message.lower(), (
            f"Error should mention first name, got: {error_message}"
        )
        logger.info("Empty first name validation works")

    async def test_empty_last_name_validation(
        self, checkout_info_page: CheckoutInfoPage
    ) -> None:
        """Verify validation for empty last name."""
        checkout_page = checkout_info_page

        await checkout_page.fill_info("John", "", "12345")
        await checkout_page.continue_checkout()

        assert await checkout_page.has_error(), "Error should be displayed"
        error_message = await checkout_page.get_error_message()
        assert "last name" in error_message.lower(), (
            f"Error should mention last name, got: {error_message}"
        )
        logger.info("Empty last name validation works")

    async def test_empty_zip_code_validation(
        self, checkout_info_page: CheckoutInfoPage
    ) -> None:
        """Verify validation for empty zip code."""
        checkout_page = checkout_info_page

        await checkout_page.fill_info("John", "Doe", "")
        await checkout_page.continue_checkout()

        assert await checkout_page.has_error(), "Error should be displayed"
        error_message = await checkout_page.get_error_message()
        assert "postal code" in error_message.lower(), (
            f"Error should mention postal code, got: {error_message}"
        )
        logger.info("Empty zip code validation works")

    async def test_cancel_checkout(
        self, checkout_info_page: CheckoutInfoPage
    ) -> None:
        """Verify cancel button returns to cart."""
        checkout_page = checkout_info_page

        await checkout_page.cancel()

        assert "/cart.html" in checkout_page.current_url, (
            "Should return to cart page"
        )
        logger.info("Cancel checkout works")


@pytest.mark.checkout
@pytest.mark.smoke
class TestCheckoutOverview:
    """Tests for checkout overview step."""

    @pytest.fixture
    async def checkout_overview_page(
        self, checkout_info_page: CheckoutInfoPage
    ) -> CheckoutOverviewPage:
        """Navigate to checkout overview."""
        user_data = generate_test_user_data()
        await checkout_info_page.fill_info(
            user_data["firstName"],
            user_data["lastName"],
            user_data["zipCode"],
        )
        await checkout_info_page.continue_checkout()

        return CheckoutOverviewPage(checkout_info_page.page)

    async def test_checkout_overview_page_loads(
        self, checkout_overview_page: CheckoutOverviewPage
    ) -> None:
        """Verify checkout overview page loads."""
        overview_page = checkout_overview_page

        assert await overview_page.is_loaded(), "Overview page should load"
        await overview_page.assert_displayed()
        logger.info("Checkout overview page loaded")

    async def test_order_items_displayed(
        self, checkout_overview_page: CheckoutOverviewPage
    ) -> None:
        """Verify order items are displayed in overview."""
        overview_page = checkout_overview_page

        items = await overview_page.get_item_names()
        assert len(items) == 2, f"Should display 2 items, got: {len(items)}"
        logger.info(f"{len(items)} order items displayed")

    async def test_pricing_information_displayed(
        self, checkout_overview_page: CheckoutOverviewPage
    ) -> None:
        """Verify all pricing information is displayed."""
        overview_page = checkout_overview_page

        subtotal = await overview_page.get_subtotal()
        tax = await overview_page.get_tax()
        total = await overview_page.get_total()

        assert subtotal > 0, "Subtotal should be positive"
        assert tax > 0, "Tax should be positive"
        assert total > 0, "Total should be positive"
        logger.info(f"Pricing displayed: Subtotal=${subtotal}, Tax=${tax}, Total=${total}")

    async def test_total_calculation(
        self, checkout_overview_page: CheckoutOverviewPage
    ) -> None:
        """Verify total equals subtotal plus tax."""
        overview_page = checkout_overview_page

        assert await overview_page.verify_total_calculation(), (
            "Total should equal subtotal + tax"
        )
        logger.info("Total calculation is correct")

    async def test_payment_and_shipping_info(
        self, checkout_overview_page: CheckoutOverviewPage
    ) -> None:
        """Verify payment and shipping information is displayed."""
        overview_page = checkout_overview_page

        payment_info = await overview_page.get_payment_info()
        shipping_info = await overview_page.get_shipping_info()

        assert len(payment_info) > 0, "Payment info should be displayed"
        assert len(shipping_info) > 0, "Shipping info should be displayed"
        logger.info("Payment and shipping info displayed")


@pytest.mark.checkout
@pytest.mark.smoke
class TestCheckoutComplete:
    """Tests for checkout completion."""

    @pytest.fixture
    async def complete_checkout(
        self, checkout_info_page: CheckoutInfoPage
    ) -> CheckoutCompletePage:
        """Complete entire checkout flow."""
        user_data = generate_test_user_data()
        await checkout_info_page.fill_info(
            user_data["firstName"],
            user_data["lastName"],
            user_data["zipCode"],
        )
        await checkout_info_page.continue_checkout()

        overview_page = CheckoutOverviewPage(checkout_info_page.page)
        await overview_page.finish()

        return CheckoutCompletePage(checkout_info_page.page)

    async def test_checkout_complete_page_loads(
        self, complete_checkout: CheckoutCompletePage
    ) -> None:
        """Verify checkout complete page loads."""
        complete_page = complete_checkout

        assert await complete_page.is_loaded(), "Complete page should load"
        await complete_page.assert_displayed()
        logger.info("Checkout complete page loaded")

    async def test_order_completion_success(
        self, complete_checkout: CheckoutCompletePage
    ) -> None:
        """Verify order completion is successful."""
        complete_page = complete_checkout

        assert await complete_page.is_order_complete(), "Order should be complete"
        await complete_page.assert_order_successful()
        logger.info("Order completed successfully")

    async def test_confirmation_messages(
        self, complete_checkout: CheckoutCompletePage
    ) -> None:
        """Verify confirmation messages are displayed."""
        complete_page = complete_checkout

        header = await complete_page.get_confirmation_header()
        message = await complete_page.get_confirmation_message()

        assert len(header) > 0, "Confirmation header should be displayed"
        assert len(message) > 0, "Confirmation message should be displayed"
        logger.info(f"Confirmation displayed: {header}")

    async def test_return_to_products(
        self, complete_checkout: CheckoutCompletePage
    ) -> None:
        """Verify back home button returns to products page."""
        complete_page = complete_checkout

        await complete_page.go_back_to_products()

        assert "/inventory.html" in complete_page.current_url, (
            "Should return to products page"
        )
        logger.info("Successfully returned to products page")
