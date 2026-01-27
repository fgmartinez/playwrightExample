"""
============================================================================
Checkout Page Objects
============================================================================
This module defines Page Objects for the SauceDemo checkout flow,
which consists of three steps:
1. Checkout Information (enter customer details)
2. Checkout Overview (review order)
3. Checkout Complete (confirmation)

Page URLs:
- https://www.saucedemo.com/checkout-step-one.html
- https://www.saucedemo.com/checkout-step-two.html
- https://www.saucedemo.com/checkout-complete.html

Usage:
    # Step 1: Information
    checkout_info = CheckoutInformationPage(page)
    await checkout_info.fill_information("John", "Doe", "12345")
    await checkout_info.continue_to_overview()

    # Step 2: Overview
    overview = CheckoutOverviewPage(page)
    await overview.finish_checkout()

    # Step 3: Complete
    complete = CheckoutCompletePage(page)
    assert await complete.is_order_complete()

Author: Your Name
Created: 2026-01-23
============================================================================
"""

from playwright.async_api import Page

from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class CheckoutInformationPage(BasePage):
    """
    Page Object for Checkout Step One - Customer Information.

    This page collects customer information (first name, last name, zip code)
    before proceeding to order review.

    Attributes:
        url: Checkout information page URL
        first_name_input: First name input field
        last_name_input: Last name input field
        zip_code_input: Postal code input field
        continue_button: Continue button
        cancel_button: Cancel button
        error_message: Error message container
    """

    def __init__(self, page: Page) -> None:
        """
        Initialize the CheckoutInformationPage.

        Args:
            page: Playwright page instance
        """
        super().__init__(page)
        self.url = "/checkout-step-one.html"

        # Page elements
        self.page_title = ".title"
        self.first_name_input = '[data-test="firstName"]'
        self.last_name_input = '[data-test="lastName"]'
        self.zip_code_input = '[data-test="postalCode"]'
        self.continue_button = '[data-test="continue"]'
        self.cancel_button = '[data-test="cancel"]'
        self.error_message = '[data-test="error"]'
        self.error_button = '.error-button'

        logger.debug("CheckoutInformationPage initialized")

    # ========================================================================
    # Form Actions
    # ========================================================================

    async def enter_first_name(self, first_name: str) -> None:
        """
        Enter first name.

        Args:
            first_name: Customer's first name
        """
        logger.debug(f"Entering first name: {first_name}")
        await self.page.locator(self.first_name_input).fill(first_name)

    async def enter_last_name(self, last_name: str) -> None:
        """
        Enter last name.

        Args:
            last_name: Customer's last name
        """
        logger.debug(f"Entering last name: {last_name}")
        await self.page.locator(self.last_name_input).fill(last_name)

    async def enter_zip_code(self, zip_code: str) -> None:
        """
        Enter postal/zip code.

        Args:
            zip_code: Postal/zip code
        """
        logger.debug(f"Entering zip code: {zip_code}")
        await self.page.locator(self.zip_code_input).fill(zip_code)

    async def fill_information(
        self,
        first_name: str,
        last_name: str,
        zip_code: str,
    ) -> None:
        """
        Fill all customer information fields.

        Args:
            first_name: Customer's first name
            last_name: Customer's last name
            zip_code: Postal/zip code
        """
        logger.info("Filling checkout information")
        await self.enter_first_name(first_name)
        await self.enter_last_name(last_name)
        await self.enter_zip_code(zip_code)

    async def continue_to_overview(self) -> None:
        """Click continue button to proceed to checkout overview."""
        logger.info("Continuing to checkout overview")
        await self.page.locator(self.continue_button).click()

    async def cancel_checkout(self) -> None:
        """Click cancel button to return to cart."""
        logger.info("Canceling checkout")
        await self.page.locator(self.cancel_button).click()

    # ========================================================================
    # Verification Methods
    # ========================================================================

    async def is_page_loaded(self) -> bool:
        """
        Verify that the checkout information page is loaded.

        Returns:
            bool: True if page is loaded
        """
        try:
            await self.page.locator(self.page_title).wait_for(state="visible", timeout=5000)
            await self.page.locator(self.first_name_input).wait_for(state="visible", timeout=5000)
            logger.debug("Checkout information page loaded")
            return True
        except Exception as e:
            logger.error(f"Checkout information page not loaded: {e}")
            return False

    async def is_error_displayed(self) -> bool:
        """
        Check if an error message is displayed.

        Returns:
            bool: True if error is visible
        """
        return await self.is_visible(self.error_message)

    async def get_error_message(self) -> str:
        """
        Get the error message text.

        Returns:
            str: Error message text
        """
        if await self.is_error_displayed():
            return await self.get_text(self.error_message)
        return ""

    async def close_error_message(self) -> None:
        """Close the error message."""
        if await self.is_error_displayed():
            logger.debug("Closing error message")
            await self.page.locator(self.error_button).click()

    # ========================================================================
    # Assertions
    # ========================================================================

    async def assert_checkout_info_page_displayed(self) -> None:
        """
        Assert that the checkout information page is displayed.

        Raises:
            AssertionError: If page is not displayed
        """
        await self.assert_element_visible(self.page_title)
        await self.assert_text_content(self.page_title, "Checkout: Your Information")
        logger.debug("Checkout information page displayed correctly")


class CheckoutOverviewPage(BasePage):
    """
    Page Object for Checkout Step Two - Order Overview.

    This page displays the order summary including items, pricing,
    and allows the user to complete the purchase.

    Attributes:
        url: Checkout overview page URL
        cart_items: Cart item containers
        subtotal: Subtotal price element
        tax: Tax amount element
        total: Total price element
        finish_button: Finish button
        cancel_button: Cancel button
    """

    def __init__(self, page: Page) -> None:
        """
        Initialize the CheckoutOverviewPage.

        Args:
            page: Playwright page instance
        """
        super().__init__(page)
        self.url = "/checkout-step-two.html"

        # Page elements
        self.page_title = ".title"
        self.cart_items = ".cart_item"
        self.payment_info = '[data-test="payment-info-value"]'
        self.shipping_info = '[data-test="shipping-info-value"]'
        self.subtotal = ".summary_subtotal_label"
        self.tax = ".summary_tax_label"
        self.total = ".summary_total_label"
        self.finish_button = '[data-test="finish"]'
        self.cancel_button = '[data-test="cancel"]'

        # Cart item elements
        self.item_name = ".inventory_item_name"
        self.item_price = ".inventory_item_price"

        logger.debug("CheckoutOverviewPage initialized")

    # ========================================================================
    # Order Review
    # ========================================================================

    async def get_order_item_names(self) -> list[str]:
        """
        Get names of all items in the order.

        Returns:
            list[str]: List of item names
        """
        elements = await self.page.locator(self.item_name).all()
        names = [await elem.text_content() for elem in elements]
        return [name.strip() for name in names if name]

    async def get_subtotal(self) -> float:
        """
        Get the order subtotal amount.

        Returns:
            float: Subtotal amount
        """
        text = await self.get_text(self.subtotal)
        # Format: "Item total: $29.99"
        amount = text.split("$")[1].strip() if "$" in text else "0"
        return float(amount)

    async def get_tax(self) -> float:
        """
        Get the tax amount.

        Returns:
            float: Tax amount
        """
        text = await self.get_text(self.tax)
        # Format: "Tax: $2.40"
        amount = text.split("$")[1].strip() if "$" in text else "0"
        return float(amount)

    async def get_total(self) -> float:
        """
        Get the order total amount.

        Returns:
            float: Total amount
        """
        text = await self.get_text(self.total)
        # Format: "Total: $32.39"
        amount = text.split("$")[1].strip() if "$" in text else "0"
        return float(amount)

    async def get_payment_info(self) -> str:
        """
        Get payment information text.

        Returns:
            str: Payment information
        """
        return await self.get_text(self.payment_info)

    async def get_shipping_info(self) -> str:
        """
        Get shipping information text.

        Returns:
            str: Shipping information
        """
        return await self.get_text(self.shipping_info)

    # ========================================================================
    # Checkout Actions
    # ========================================================================

    async def finish_checkout(self) -> None:
        """Click finish button to complete the order."""
        logger.info("Finishing checkout")
        await self.page.locator(self.finish_button).click()

    async def cancel_checkout(self) -> None:
        """Click cancel button to return to products page."""
        logger.info("Canceling checkout")
        await self.page.locator(self.cancel_button).click()

    # ========================================================================
    # Verification Methods
    # ========================================================================

    async def is_page_loaded(self) -> bool:
        """
        Verify that the checkout overview page is loaded.

        Returns:
            bool: True if page is loaded
        """
        try:
            await self.page.locator(self.page_title).wait_for(state="visible", timeout=5000)
            await self.page.locator(self.finish_button).wait_for(state="visible", timeout=5000)
            logger.debug("Checkout overview page loaded")
            return True
        except Exception as e:
            logger.error(f"Checkout overview page not loaded: {e}")
            return False

    async def verify_total_calculation(self) -> bool:
        """
        Verify that total equals subtotal plus tax.

        Returns:
            bool: True if calculation is correct
        """
        subtotal = await self.get_subtotal()
        tax = await self.get_tax()
        total = await self.get_total()

        expected_total = round(subtotal + tax, 2)
        actual_total = round(total, 2)

        is_correct = expected_total == actual_total

        if is_correct:
            logger.debug(f"Total calculation correct: {subtotal} + {tax} = {total}")
        else:
            logger.warning(
                f"Total calculation incorrect. Expected: {expected_total}, Got: {actual_total}"
            )

        return is_correct

    # ========================================================================
    # Assertions
    # ========================================================================

    async def assert_checkout_overview_page_displayed(self) -> None:
        """
        Assert that the checkout overview page is displayed.

        Raises:
            AssertionError: If page is not displayed
        """
        await self.assert_element_visible(self.page_title)
        await self.assert_text_content(self.page_title, "Checkout: Overview")
        logger.debug("Checkout overview page displayed correctly")


class CheckoutCompletePage(BasePage):
    """
    Page Object for Checkout Complete - Order Confirmation.

    This page displays the order confirmation after successful checkout.

    Attributes:
        url: Checkout complete page URL
        complete_header: Confirmation header
        complete_text: Confirmation message
        back_home_button: Back to products button
    """

    def __init__(self, page: Page) -> None:
        """
        Initialize the CheckoutCompletePage.

        Args:
            page: Playwright page instance
        """
        super().__init__(page)
        self.url = "/checkout-complete.html"

        # Page elements
        self.page_title = ".title"
        self.complete_header = ".complete-header"
        self.complete_text = ".complete-text"
        self.pony_express_image = ".pony_express"
        self.back_home_button = '[data-test="back-to-products"]'

        logger.debug("CheckoutCompletePage initialized")

    # ========================================================================
    # Navigation Actions
    # ========================================================================

    async def go_back_to_products(self) -> None:
        """Click back home button to return to products page."""
        logger.info("Returning to products page")
        await self.page.locator(self.back_home_button).click()

    # ========================================================================
    # Verification Methods
    # ========================================================================

    async def is_page_loaded(self) -> bool:
        """
        Verify that the checkout complete page is loaded.

        Returns:
            bool: True if page is loaded
        """
        try:
            await self.page.locator(self.page_title).wait_for(state="visible", timeout=5000)
            await self.page.locator(self.complete_header).wait_for(state="visible", timeout=5000)
            logger.debug("Checkout complete page loaded")
            return True
        except Exception as e:
            logger.error(f"Checkout complete page not loaded: {e}")
            return False

    async def is_order_complete(self) -> bool:
        """
        Check if the order was completed successfully.

        Returns:
            bool: True if success message is displayed
        """
        try:
            header_text = await self.get_text(self.complete_header)
            return "thank you" in header_text.lower() or "complete" in header_text.lower()
        except Exception:
            return False

    async def get_confirmation_header(self) -> str:
        """
        Get the confirmation header text.

        Returns:
            str: Confirmation header text
        """
        return await self.get_text(self.complete_header)

    async def get_confirmation_message(self) -> str:
        """
        Get the confirmation message text.

        Returns:
            str: Confirmation message
        """
        return await self.get_text(self.complete_text)

    # ========================================================================
    # Assertions
    # ========================================================================

    async def assert_checkout_complete_page_displayed(self) -> None:
        """
        Assert that the checkout complete page is displayed.

        Raises:
            AssertionError: If page is not displayed
        """
        await self.assert_element_visible(self.page_title)
        await self.assert_text_content(self.page_title, "Checkout: Complete!")
        logger.debug("Checkout complete page displayed correctly")

    async def assert_order_successful(self) -> None:
        """
        Assert that the order was completed successfully.

        Raises:
            AssertionError: If order was not successful
        """
        assert await self.is_order_complete(), "Order should be completed successfully"
        await self.assert_element_visible(self.complete_header)
        await self.assert_element_visible(self.pony_express_image)
        logger.debug("Order completed successfully")
