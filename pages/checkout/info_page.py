"""Checkout step one page object (customer information form)."""

import logging

from playwright.sync_api import Page

from pages.base_page import AuthenticatedPage
from pages.components.error_banner import ErrorBanner

logger = logging.getLogger(__name__)


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
