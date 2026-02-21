"""
Checkout Page Objects
=====================
Page objects for the SauceDemo checkout flow:
1. CheckoutInfoPage - Enter customer information
2. CheckoutOverviewPage - Review order before purchase
3. CheckoutCompletePage - Order confirmation
"""

from playwright.async_api import Page, expect

from config import settings
from pages.components import CartItem, PriceSummary
from pages.navigator import PageNavigator, get_text, is_visible_safe
from utils.logger import get_logger

logger = get_logger(__name__)


class CheckoutInfoPage:
    """Page object for checkout step one - customer information."""

    URL = "/checkout-step-one.html"

    def __init__(self, page: Page) -> None:
        self.page = page
        self._nav = PageNavigator(page, settings.test.default_timeout)
        logger.debug("Initialized CheckoutInfoPage")

        # Page elements
        self.title = page.locator(".title")

        # Form fields
        self.first_name = page.get_by_test_id("firstName")
        self.last_name = page.get_by_test_id("lastName")
        self.postal_code = page.get_by_test_id("postalCode")

        # Buttons
        self.continue_button = page.get_by_test_id("continue")
        self.cancel_button = page.get_by_test_id("cancel")

        # Error
        self.error_container = page.get_by_test_id("error")
        self.error_close_button = page.locator(".error-button")

    # ========================================================================
    # Navigation
    # ========================================================================

    async def navigate(self) -> None:
        """Navigate to the checkout info page."""
        await self._nav.go(self.URL)

    async def wait_for_page_load(self) -> None:
        """Wait for page to be fully loaded."""
        await self._nav.wait_for_load()

    # ========================================================================
    # Form Actions
    # ========================================================================

    async def fill_info(self, first_name: str, last_name: str, postal_code: str) -> None:
        """Fill all customer information fields."""
        logger.info("Filling checkout information")
        await self.first_name.fill(first_name)
        await self.last_name.fill(last_name)
        await self.postal_code.fill(postal_code)

    async def continue_checkout(self) -> None:
        """Click continue to proceed to overview."""
        logger.info("Continuing to overview")
        await self.continue_button.click()

    async def cancel(self) -> None:
        """Cancel checkout and return to cart."""
        logger.info("Canceling checkout")
        await self.cancel_button.click()

    async def close_error(self) -> None:
        """Close error message if visible."""
        if await is_visible_safe(self.error_container):
            await self.error_close_button.click()

    # ========================================================================
    # State Checks
    # ========================================================================

    async def has_error(self) -> bool:
        """Check if error is displayed."""
        return await is_visible_safe(self.error_container)

    async def get_error_message(self) -> str:
        """Get error message text."""
        if await self.has_error():
            return await get_text(self.error_container)
        return ""

    async def is_loaded(self) -> bool:
        """Check if page is loaded."""
        try:
            await self.title.wait_for(state="visible", timeout=5000)
            await self.first_name.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False

    # ========================================================================
    # Assertions
    # ========================================================================

    async def assert_displayed(self) -> None:
        """Assert checkout info page is displayed."""
        await expect(self.title).to_be_visible()
        await expect(self.title).to_contain_text("Checkout: Your Information")


class CheckoutOverviewPage:
    """Page object for checkout step two - order overview."""

    URL = "/checkout-step-two.html"

    def __init__(self, page: Page) -> None:
        self.page = page
        self._nav = PageNavigator(page, settings.test.default_timeout)
        logger.debug("Initialized CheckoutOverviewPage")

        # Page elements
        self.title = page.locator(".title")

        # Summary info
        self.payment_info = page.get_by_test_id("payment-info-value")
        self.shipping_info = page.get_by_test_id("shipping-info-value")
        self.subtotal_label = page.locator(".summary_subtotal_label")
        self.tax_label = page.locator(".summary_tax_label")
        self.total_label = page.locator(".summary_total_label")

        # Buttons
        self.finish_button = page.get_by_test_id("finish")
        self.cancel_button = page.get_by_test_id("cancel")

        # Cart items
        self._cart_items = CartItem.all_items(page)

    # ========================================================================
    # Navigation
    # ========================================================================

    async def navigate(self) -> None:
        """Navigate to the checkout overview page."""
        await self._nav.go(self.URL)

    async def wait_for_page_load(self) -> None:
        """Wait for page to be fully loaded."""
        await self._nav.wait_for_load()

    # ========================================================================
    # Order Items
    # ========================================================================

    async def get_all_items(self) -> list[CartItem]:
        """Get all items in order."""
        items = await self._cart_items.all()
        return [CartItem(item) for item in items]

    async def get_item_names(self) -> list[str]:
        """Get names of all items in order."""
        items = await self.get_all_items()
        return [await item.get_name() for item in items]

    # ========================================================================
    # Pricing
    # ========================================================================

    async def _parse_price(self, text: str) -> float:
        """Extract price from text like 'Item total: $29.99'."""
        if "$" in text:
            return float(text.split("$")[1].strip())
        return 0.0

    async def get_subtotal(self) -> float:
        """Get order subtotal."""
        text = await get_text(self.subtotal_label)
        return await self._parse_price(text)

    async def get_tax(self) -> float:
        """Get tax amount."""
        text = await get_text(self.tax_label)
        return await self._parse_price(text)

    async def get_total(self) -> float:
        """Get order total."""
        text = await get_text(self.total_label)
        return await self._parse_price(text)

    async def get_price_summary(self) -> PriceSummary:
        """Get complete price summary."""
        return PriceSummary(
            subtotal=await self.get_subtotal(),
            tax=await self.get_tax(),
            total=await self.get_total(),
        )

    async def get_payment_info(self) -> str:
        """Get payment information text."""
        return await get_text(self.payment_info)

    async def get_shipping_info(self) -> str:
        """Get shipping information text."""
        return await get_text(self.shipping_info)

    # ========================================================================
    # Actions
    # ========================================================================

    async def finish(self) -> None:
        """Complete the order."""
        logger.info("Finishing checkout")
        await self.finish_button.click()

    async def cancel(self) -> None:
        """Cancel and return to products."""
        logger.info("Canceling checkout")
        await self.cancel_button.click()

    # ========================================================================
    # State Checks
    # ========================================================================

    async def is_loaded(self) -> bool:
        """Check if page is loaded."""
        try:
            await self.title.wait_for(state="visible", timeout=5000)
            await self.finish_button.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False

    async def verify_total_calculation(self) -> bool:
        """Verify total equals subtotal + tax."""
        summary = await self.get_price_summary()
        return summary.verify_calculation()

    # ========================================================================
    # Assertions
    # ========================================================================

    async def assert_displayed(self) -> None:
        """Assert overview page is displayed."""
        await expect(self.title).to_be_visible()
        await expect(self.title).to_contain_text("Checkout: Overview")


class CheckoutCompletePage:
    """Page object for checkout complete - order confirmation."""

    URL = "/checkout-complete.html"

    def __init__(self, page: Page) -> None:
        self.page = page
        self._nav = PageNavigator(page, settings.test.default_timeout)
        logger.debug("Initialized CheckoutCompletePage")

        # Page elements
        self.title = page.locator(".title")
        self.complete_header = page.locator(".complete-header")
        self.complete_text = page.locator(".complete-text")
        self.pony_image = page.locator(".pony_express")
        self.back_button = page.get_by_test_id("back-to-products")

    # ========================================================================
    # Navigation
    # ========================================================================

    async def navigate(self) -> None:
        """Navigate to the checkout complete page."""
        await self._nav.go(self.URL)

    async def wait_for_page_load(self) -> None:
        """Wait for page to be fully loaded."""
        await self._nav.wait_for_load()

    # ========================================================================
    # Actions
    # ========================================================================

    async def go_back_to_products(self) -> None:
        """Return to products page."""
        logger.info("Returning to products")
        await self.back_button.click()

    # ========================================================================
    # State Checks
    # ========================================================================

    async def is_order_complete(self) -> bool:
        """Check if order completed successfully."""
        try:
            header = await get_text(self.complete_header)
            return "thank you" in header.lower()
        except Exception:
            return False

    async def get_confirmation_header(self) -> str:
        """Get confirmation header text."""
        return await get_text(self.complete_header)

    async def get_confirmation_message(self) -> str:
        """Get confirmation message text."""
        return await get_text(self.complete_text)

    async def is_loaded(self) -> bool:
        """Check if page is loaded."""
        try:
            await self.title.wait_for(state="visible", timeout=5000)
            await self.complete_header.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False

    # ========================================================================
    # Assertions
    # ========================================================================

    async def assert_displayed(self) -> None:
        """Assert complete page is displayed."""
        await expect(self.title).to_be_visible()
        await expect(self.title).to_contain_text("Checkout: Complete!")

    async def assert_order_successful(self) -> None:
        """Assert order completed successfully."""
        assert await self.is_order_complete(), "Order should be complete"
        await expect(self.complete_header).to_be_visible()
        await expect(self.pony_image).to_be_visible()
