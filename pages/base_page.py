"""
Base Page Object - Modern Playwright Pattern
=============================================
Provides common functionality for all page objects using Playwright's
native locator API. Page objects should define elements as Locators
in __init__ for clean, chainable interactions.

Design Principles:
- Elements defined as Locators, not strings
- Use semantic locators (get_by_test_id, get_by_role) when possible
- Assertions use Playwright's expect API
- Minimal abstraction - leverage Playwright's native API

Usage:
    class MyPage(BasePage):
        def __init__(self, page: Page):
            super().__init__(page)
            self.url = "/my-page"
            self.submit_button = page.get_by_role("button", name="Submit")
            self.email_input = page.get_by_test_id("email")

        async def submit_form(self, email: str):
            await self.email_input.fill(email)
            await self.submit_button.click()
"""

from playwright.async_api import Locator, Page, expect

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class BasePage:
    """
    Base class for all page objects.

    Provides navigation, page load handling, and common utilities.
    Child classes should define elements as Locators in __init__.
    """

    def __init__(self, page: Page) -> None:
        self.page = page
        self.url: str = ""
        self.timeout: int = settings.test.default_timeout
        logger.debug(f"Initialized {self.__class__.__name__}")

    # ========================================================================
    # Navigation
    # ========================================================================

    async def navigate(self, path: str | None = None) -> None:
        """Navigate to the page URL and wait for load."""
        target_url = f"{settings.base_url}{path or self.url}"
        logger.info(f"Navigating to: {target_url}")
        await self.page.goto(target_url, wait_until="domcontentloaded")
        await self.wait_for_page_load()

    async def wait_for_page_load(self) -> None:
        """Wait for page to be fully loaded (load + networkidle)."""
        try:
            await self.page.wait_for_load_state("load", timeout=self.timeout)
            await self.page.wait_for_load_state("networkidle", timeout=self.timeout)
            logger.debug("Page fully loaded")
        except Exception as e:
            logger.warning(f"Page load timeout: {e}")

    async def reload(self) -> None:
        """Reload the current page."""
        logger.info("Reloading page")
        await self.page.reload(wait_until="domcontentloaded")
        await self.wait_for_page_load()

    # ========================================================================
    # Locator Utilities
    # ========================================================================

    async def get_all_texts(self, locator: Locator) -> list[str]:
        """
        Get text content from all matching elements, stripped.

        Args:
            locator: Playwright locator matching multiple elements

        Returns:
            List of stripped text content
        """
        elements = await locator.all()
        texts = [await el.text_content() for el in elements]
        return [t.strip() for t in texts if t]

    async def get_text(self, locator: Locator) -> str:
        """Get text content from element, stripped."""
        text = await locator.text_content()
        return (text or "").strip()

    async def is_visible_safe(self, locator: Locator) -> bool:
        """Check visibility without throwing on missing elements."""
        try:
            return await locator.is_visible()
        except Exception:
            return False

    # ========================================================================
    # Assertions (using Playwright's expect API)
    # ========================================================================

    async def assert_visible(self, locator: Locator) -> None:
        """Assert element is visible."""
        await expect(locator).to_be_visible()

    async def assert_hidden(self, locator: Locator) -> None:
        """Assert element is hidden."""
        await expect(locator).to_be_hidden()

    async def assert_has_text(self, locator: Locator, text: str) -> None:
        """Assert element contains text."""
        await expect(locator).to_contain_text(text)

    async def assert_has_value(self, locator: Locator, value: str) -> None:
        """Assert input has value."""
        await expect(locator).to_have_value(value)

    # ========================================================================
    # Debugging
    # ========================================================================

    async def take_screenshot(self, name: str, full_page: bool = False) -> None:
        """Capture a screenshot."""
        from utils.helpers import take_screenshot
        await take_screenshot(self.page, name, full_page=full_page)

    async def highlight(self, locator: Locator, duration: int = 1000) -> None:
        """Highlight an element for debugging."""
        await locator.evaluate(
            """(el, ms) => {
                const original = el.style.outline;
                el.style.outline = '3px solid red';
                setTimeout(() => el.style.outline = original, ms);
            }""",
            duration
        )
