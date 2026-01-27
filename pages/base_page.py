"""
============================================================================
Base Page Object
============================================================================
This module defines the BasePage class, which serves as the parent class
for all page objects in the framework. It provides common functionality
shared across all pages.

Key Features:
- Page navigation with base URL handling
- Page load state management
- Common assertions using Playwright's expect API
- Utility methods that add value beyond Playwright's native API

Design Pattern:
This follows the Page Object Model (POM) pattern where each page is
represented by a class that encapsulates the page's structure and behavior.

Note: This class intentionally does NOT wrap Playwright's native methods
like locator(), click(), fill(), etc. Page objects should use self.page
directly to leverage Playwright's full API and avoid unnecessary abstraction.

Usage:
    class MyPage(BasePage):
        def __init__(self, page: Page):
            super().__init__(page)
            self.url = "/my-page"

        async def click_submit(self):
            await self.page.locator("#submit").click()

Author: Your Name
Created: 2026-01-23
============================================================================
"""

from playwright.async_api import Page, expect

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class BasePage:
    """
    Base class for all page objects.

    This class provides common functionality that adds value beyond
    Playwright's native API, such as navigation with base URL handling,
    page load management, and assertion helpers.

    For element interactions, use self.page directly to access
    Playwright's native API (locator, click, fill, etc.).

    Attributes:
        page: Playwright page instance
        url: Relative URL path for this page
        timeout: Default timeout for operations
    """

    def __init__(self, page: Page) -> None:
        """
        Initialize the base page.

        Args:
            page: Playwright page instance
        """
        self.page = page
        self.url: str = ""  # Override in subclasses
        self.timeout: int = settings.test.default_timeout
        logger.debug(f"Initialized {self.__class__.__name__}")

    # ========================================================================
    # Navigation Methods
    # ========================================================================

    async def navigate(self, path: str | None = None) -> None:
        """
        Navigate to the page URL.

        Args:
            path: Optional path to append to base URL (uses self.url if not provided)

        Example:
            >>> await page.navigate()  # Uses self.url
            >>> await page.navigate("/custom-path")
        """
        target_url = f"{settings.base_url}{path or self.url}"
        logger.info(f"Navigating to: {target_url}")
        await self.page.goto(target_url, wait_until="domcontentloaded")
        await self.wait_for_page_load()

    async def wait_for_page_load(self) -> None:
        """
        Wait for the page to be fully loaded.

        This waits for both the 'load' event and network to be idle.
        """
        try:
            await self.page.wait_for_load_state("load", timeout=self.timeout)
            await self.page.wait_for_load_state("networkidle", timeout=self.timeout)
            logger.debug("Page fully loaded")
        except Exception as e:
            logger.warning(f"Page load timeout: {e}")

    async def reload(self) -> None:
        """Reload the current page and wait for it to load."""
        logger.info("Reloading page")
        await self.page.reload(wait_until="domcontentloaded")
        await self.wait_for_page_load()

    async def go_back(self) -> None:
        """Navigate back in browser history."""
        logger.info("Navigating back")
        await self.page.go_back(wait_until="domcontentloaded")

    async def go_forward(self) -> None:
        """Navigate forward in browser history."""
        logger.info("Navigating forward")
        await self.page.go_forward(wait_until="domcontentloaded")

    # ========================================================================
    # Utility Methods (add value beyond Playwright's native API)
    # ========================================================================

    async def get_text(self, selector: str) -> str:
        """
        Get text content of an element, stripped of whitespace.

        Args:
            selector: Element selector

        Returns:
            str: Element text content, stripped
        """
        text = await self.page.locator(selector).text_content()
        return (text or "").strip()

    async def is_visible(self, selector: str) -> bool:
        """
        Check if an element is visible, returning False on any error.

        This is useful for conditional checks where you don't want
        exceptions thrown for missing elements.

        Args:
            selector: Element selector

        Returns:
            bool: True if visible, False otherwise (including errors)
        """
        try:
            return await self.page.locator(selector).is_visible()
        except Exception:
            return False

    async def scroll_to(self, selector: str) -> None:
        """
        Scroll an element into view.

        Args:
            selector: Element selector
        """
        logger.debug(f"Scrolling to: {selector}")
        await self.page.locator(selector).scroll_into_view_if_needed()

    # ========================================================================
    # Assertion Helpers
    # ========================================================================

    async def assert_element_visible(self, selector: str) -> None:
        """
        Assert that an element is visible.

        Args:
            selector: Element selector
        """
        await expect(self.page.locator(selector)).to_be_visible()
        logger.debug(f"Verified '{selector}' is visible")

    async def assert_element_hidden(self, selector: str) -> None:
        """
        Assert that an element is hidden.

        Args:
            selector: Element selector
        """
        await expect(self.page.locator(selector)).to_be_hidden()
        logger.debug(f"Verified '{selector}' is hidden")

    async def assert_text_content(self, selector: str, expected_text: str) -> None:
        """
        Assert that an element contains expected text.

        Args:
            selector: Element selector
            expected_text: Expected text content
        """
        await expect(self.page.locator(selector)).to_contain_text(expected_text)
        logger.debug(f"Verified '{selector}' contains text: {expected_text}")

    async def assert_url_contains(self, url_part: str) -> None:
        """
        Assert that current URL contains specified text.

        Args:
            url_part: Text that should be in the URL
        """
        await expect(self.page).to_have_url(url_part)
        logger.debug(f"Verified URL contains: {url_part}")

    # ========================================================================
    # Screenshot and Debugging
    # ========================================================================

    async def take_screenshot(self, name: str, full_page: bool = False) -> None:
        """
        Capture a screenshot of the page.

        Args:
            name: Screenshot file name
            full_page: Capture full scrollable page
        """
        from utils.helpers import take_screenshot

        await take_screenshot(self.page, name, full_page=full_page)

    async def highlight_element(self, selector: str, duration: int = 1000) -> None:
        """
        Highlight an element (useful for debugging).

        Args:
            selector: Element selector
            duration: Highlight duration in milliseconds
        """
        from utils.helpers import highlight_element

        await highlight_element(self.page, selector, duration=duration)
