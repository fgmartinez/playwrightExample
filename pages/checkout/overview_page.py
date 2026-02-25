"""Checkout step two page object (order overview and pricing)."""

import logging

from playwright.sync_api import Page

from pages.base_page import AuthenticatedPage
from pages.components.cart_item import CartItem
from pages.components.price_summary import PriceSummary
from pages.page_helpers import get_text

logger = logging.getLogger(__name__)


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

    def get_all_items(self) -> list[CartItem]:
        items = self._cart_items.all()
        return [CartItem(item) for item in items]

    def get_item_names(self) -> list[str]:
        return [item.get_name() for item in self.get_all_items()]

    @staticmethod
    def _parse_price(text: str) -> float:
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

    def finish(self) -> None:
        logger.info("Finishing checkout")
        self.finish_button.click()

    def cancel(self) -> None:
        logger.info("Canceling checkout")
        self.cancel_button.click()

    def is_loaded(self) -> bool:
        try:
            self.title.wait_for(state="visible", timeout=5000)
            self.finish_button.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False

    def verify_total_calculation(self) -> bool:
        return self.get_price_summary().verify_calculation()
