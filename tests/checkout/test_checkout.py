"""Checkout tests -- information form, overview, and completion."""

import pytest
from playwright.sync_api import expect

from pages import CheckoutCompletePage, CheckoutInfoPage, CheckoutOverviewPage
from utils.helpers import generate_test_user_data

import logging

logger = logging.getLogger(__name__)


@pytest.mark.checkout
@pytest.mark.smoke
class TestCheckoutInformation:
    """Form validation on the checkout-info page."""

    def test_page_loads(self, checkout_info_page: CheckoutInfoPage) -> None:
        """Checkout information page loads with the correct title."""
        assert checkout_info_page.is_loaded()
        expect(checkout_info_page.title).to_contain_text("Checkout: Your Information")

    def test_fill_valid_information(
        self, checkout_info_page: CheckoutInfoPage, user_data: dict[str, str]
    ) -> None:
        """Valid data advances to the overview step."""
        checkout_info_page.fill_info(
            user_data["firstName"], user_data["lastName"], user_data["zipCode"]
        )
        checkout_info_page.continue_checkout()
        assert "/checkout-step-two.html" in checkout_info_page.current_url

    @pytest.mark.parametrize(
        "first, last, zip_code, keyword",
        [
            ("", "Doe", "12345", "first name"),
            ("John", "", "12345", "last name"),
            ("John", "Doe", "", "postal code"),
        ],
        ids=["missing-first", "missing-last", "missing-zip"],
    )
    def test_empty_field_validation(
        self,
        checkout_info_page: CheckoutInfoPage,
        first: str,
        last: str,
        zip_code: str,
        keyword: str,
    ) -> None:
        """Each required field triggers an error mentioning the missing field."""
        checkout_info_page.fill_info(first, last, zip_code)
        checkout_info_page.continue_checkout()

        assert checkout_info_page.error.is_visible()
        msg = checkout_info_page.error.get_message()
        assert keyword in msg.lower()

    def test_cancel_returns_to_cart(
        self, checkout_info_page: CheckoutInfoPage
    ) -> None:
        """Cancel button returns to the cart."""
        checkout_info_page.cancel()
        assert "/cart.html" in checkout_info_page.current_url


@pytest.mark.checkout
@pytest.mark.smoke
class TestCheckoutOverview:
    """Order review before completing the purchase."""

    @pytest.fixture
    def overview_page(
        self, checkout_info_page: CheckoutInfoPage
    ) -> CheckoutOverviewPage:
        """Navigate through info step to reach the overview."""
        data = generate_test_user_data()
        checkout_info_page.fill_info(data["firstName"], data["lastName"], data["zipCode"])
        checkout_info_page.continue_checkout()
        return CheckoutOverviewPage(checkout_info_page.page)

    def test_overview_displays_items_and_pricing(
        self, overview_page: CheckoutOverviewPage
    ) -> None:
        """Overview shows the ordered items and positive pricing values."""
        assert overview_page.is_loaded()
        expect(overview_page.title).to_contain_text("Checkout: Overview")

        items = overview_page.get_item_names()
        assert len(items) == 2

        summary = overview_page.get_price_summary()
        assert summary.subtotal > 0
        assert summary.tax > 0
        assert summary.total > 0
        assert summary.verify_calculation()


@pytest.mark.checkout
@pytest.mark.smoke
class TestCheckoutComplete:
    """Order confirmation screen."""

    @pytest.fixture
    def complete_page(
        self, checkout_info_page: CheckoutInfoPage
    ) -> CheckoutCompletePage:
        """Complete the entire checkout flow."""
        data = generate_test_user_data()
        checkout_info_page.fill_info(data["firstName"], data["lastName"], data["zipCode"])
        checkout_info_page.continue_checkout()

        overview = CheckoutOverviewPage(checkout_info_page.page)
        overview.finish()
        return CheckoutCompletePage(checkout_info_page.page)

    def test_order_completed_successfully(
        self, complete_page: CheckoutCompletePage
    ) -> None:
        """Confirmation page shows a thank-you header and pony image."""
        assert complete_page.is_loaded()
        assert complete_page.is_order_complete()
        expect(complete_page.complete_header).to_be_visible()
        expect(complete_page.pony_image).to_be_visible()

        header = complete_page.get_confirmation_header()
        message = complete_page.get_confirmation_message()
        assert header
        assert message

    def test_back_to_products(self, complete_page: CheckoutCompletePage) -> None:
        """Back-home button returns to the products page."""
        complete_page.go_back_to_products()
        assert "/inventory.html" in complete_page.current_url
