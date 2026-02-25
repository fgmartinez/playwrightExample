"""Checkout step three page object (order confirmation)."""

import logging

from playwright.sync_api import Page

from pages.base_page import AuthenticatedPage
from pages.page_helpers import get_text

logger = logging.getLogger(__name__)


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
            self.complete_header.wait_for(state="visible", timeout=5000)
            return "thank you" in get_text(self.complete_header).lower()
        except Exception:
            return False

    def get_confirmation_header(self) -> str:
        return get_text(self.complete_header)

    def get_confirmation_message(self) -> str:
        return get_text(self.complete_text)

    def is_loaded(self) -> bool:
        try:
            self.complete_header.wait_for(state="visible", timeout=5000)
            self.back_button.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False
