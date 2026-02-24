"""Checkout page objects for the three-step checkout flow.

1. ``CheckoutInfoPage``     -- enter customer information
2. ``CheckoutOverviewPage`` -- review the order
3. ``CheckoutCompletePage`` -- confirmation screen
"""

import logging

from playwright.sync_api import Page

from pages.base_page import AuthenticatedPage
from pages.components.cart_item import CartItem
from pages.components.error_banner import ErrorBanner
from pages.components.price_summary import PriceSummary
from pages.page_helpers import get_text

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Step 1 -- Customer information
# ---------------------------------------------------------------------------


class CheckoutInfoPage(AuthenticatedPage):
    """Checkout step one -- enter first name, last name, postal code."""

    URL = "/checkout-step-one.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.first_name = page.get_by_test_id("firstName")
        self.last_name = page.get_by_test_id("lastName")
        self.postal_code = page.get_by_test_id("postalCode")
        self.continue_button = page.get_by_test_id("continue")
        self.cancel_button = page.get_by_test_id("cancel")
        self.error = ErrorBanner(page)

    def fill_info(self, first_name: str, last_name: str, postal_code: str) -> None:
        logger.info("Filling checkout information")
        self.first_name.fill(first_name)
        self.last_name.fill(last_name)
        self.postal_code.fill(postal_code)

    def continue_checkout(self) -> None:
        logger.info("Continuing to overview")
        self.continue_button.click()

    def cancel(self) -> None:
        logger.info("Canceling checkout")
        self.cancel_button.click()

    def is_loaded(self) -> bool:
        try:
            self.title.wait_for(state="visible", timeout=5000)
            self.first_name.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Step 2 -- Order overview
# ---------------------------------------------------------------------------


class CheckoutOverviewPage(AuthenticatedPage):
    """Checkout step two -- review items, pricing, and shipping info."""

    URL = "/checkout-step-two.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.payment_info = page.get_by_test_id("payment-info-value")
        self.shipping_info = page.get_by_test_id("shipping-info-value")
        self.subtotal_label = page.locator(".summary_subtotal_label")
        self.tax_label = page.locator(".summary_tax_label")
        self.total_label = page.locator(".summary_total_label")
        self.finish_button = page.get_by_test_id("finish")
        self.cancel_button = page.get_by_test_id("cancel")
        self._cart_items = CartItem.all_items(page)

    # -- Order items ---------------------------------------------------------

    def get_all_items(self) -> list[CartItem]:
        items = self._cart_items.all()
        return [CartItem(item) for item in items]

    def get_item_names(self) -> list[str]:
        return [item.get_name() for item in self.get_all_items()]

    # -- Pricing -------------------------------------------------------------

    @staticmethod
    def _parse_price(text: str) -> float:
        """Extract the dollar amount from text like ``Item total: $29.99``."""
        if "$" in text:
            return float(text.split("$")[1].strip())
        return 0.0

    def get_subtotal(self) -> float:
        return self._parse_price(get_text(self.subtotal_label))

    def get_tax(self) -> float:
        return self._parse_price(get_text(self.tax_label))

    def get_total(self) -> float:
        return self._parse_price(get_text(self.total_label))

    def get_price_summary(self) -> PriceSummary:
        return PriceSummary(
            subtotal=self.get_subtotal(),
            tax=self.get_tax(),
            total=self.get_total(),
        )

    def get_payment_info(self) -> str:
        return get_text(self.payment_info)

    def get_shipping_info(self) -> str:
        return get_text(self.shipping_info)

    # -- Actions -------------------------------------------------------------

    def finish(self) -> None:
        logger.info("Finishing checkout")
        self.finish_button.click()

    def cancel(self) -> None:
        logger.info("Canceling checkout")
        self.cancel_button.click()

    # -- Page state ----------------------------------------------------------

    def is_loaded(self) -> bool:
        try:
            self.title.wait_for(state="visible", timeout=5000)
            self.finish_button.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False

    def verify_total_calculation(self) -> bool:
        summary = self.get_price_summary()
        return summary.verify_calculation()


# ---------------------------------------------------------------------------
# Step 3 -- Confirmation
# ---------------------------------------------------------------------------


class CheckoutCompletePage(AuthenticatedPage):
    """Checkout complete -- order confirmation screen."""

    URL = "/checkout-complete.html"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.complete_header = page.locator(".complete-header")
        self.complete_text = page.locator(".complete-text")
        self.pony_image = page.locator(".pony_express")
        self.back_button = page.get_by_test_id("back-to-products")

    def go_back_to_products(self) -> None:
        logger.info("Returning to products")
        self.back_button.click()

    def is_order_complete(self) -> bool:
        try:
            header = get_text(self.complete_header)
            return "thank you" in header.lower()
        except Exception:
            return False

    def get_confirmation_header(self) -> str:
        return get_text(self.complete_header)

    def get_confirmation_message(self) -> str:
        return get_text(self.complete_text)

    def is_loaded(self) -> bool:
        try:
            self.title.wait_for(state="visible", timeout=5000)
            self.complete_header.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False
