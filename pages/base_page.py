"""
============================================================================
Base Page Object
============================================================================
This module defines the BasePage class, which serves as the parent class
for all page objects in the framework. It provides common functionality
shared across all pages.

Key Features:
- Page navigation
- Element waiting and interaction
- Screenshot capture
- Logging
- Error handling
- Common assertions

Design Pattern:
This follows the Page Object Model (POM) pattern where each page is
represented by a class that encapsulates the page's structure and behavior.

Usage:
    class MyPage(BasePage):
        def __init__(self, page: Page):
            super().__init__(page)
            self.url = "/my-page"

        async def do_something(self):
            await self.click_element(self.locator("button"))

Author: Your Name
Created: 2026-01-23
============================================================================
"""

from typing import Any

from playwright.async_api import Locator, Page, expect

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class BasePage:
    """
    Base class for all page objects.

    This class provides common functionality that all pages need, such as
    navigation, element waiting, clicking, typing, and assertions.

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
        """
        Reload the current page.

        Example:
            >>> await page.reload()
        """
        logger.info("Reloading page")
        await self.page.reload(wait_until="domcontentloaded")
        await self.wait_for_page_load()

    async def go_back(self) -> None:
        """
        Navigate back in browser history.

        Example:
            >>> await page.go_back()
        """
        logger.info("Navigating back")
        await self.page.go_back(wait_until="domcontentloaded")

    async def go_forward(self) -> None:
        """
        Navigate forward in browser history.

        Example:
            >>> await page.go_forward()
        """
        logger.info("Navigating forward")
        await self.page.go_forward(wait_until="domcontentloaded")

    @property
    def current_url(self) -> str:
        """
        Get the current page URL.

        Returns:
            str: Current URL

        Example:
            >>> url = page.current_url
        """
        return self.page.url

    # ========================================================================
    # Locator Methods
    # ========================================================================

    def locator(self, selector: str) -> Locator:
        """
        Get a locator for the given selector.

        Args:
            selector: CSS selector, text selector, or other Playwright selector

        Returns:
            Locator: Playwright locator instance

        Example:
            >>> login_button = page.locator("#login-button")
            >>> await login_button.click()
        """
        return self.page.locator(selector)

    def get_by_role(self, role: str, **kwargs: Any) -> Locator:
        """
        Get element by ARIA role.

        Args:
            role: ARIA role name
            **kwargs: Additional options (name, exact, etc.)

        Returns:
            Locator: Playwright locator instance

        Example:
            >>> button = page.get_by_role("button", name="Submit")
        """
        return self.page.get_by_role(role, **kwargs)

    def get_by_text(self, text: str, exact: bool = False) -> Locator:
        """
        Get element by text content.

        Args:
            text: Text to search for
            exact: Whether to match exact text

        Returns:
            Locator: Playwright locator instance

        Example:
            >>> heading = page.get_by_text("Welcome", exact=True)
        """
        return self.page.get_by_text(text, exact=exact)

    def get_by_label(self, text: str) -> Locator:
        """
        Get form input by associated label text.

        Args:
            text: Label text

        Returns:
            Locator: Playwright locator instance

        Example:
            >>> email_input = page.get_by_label("Email Address")
        """
        return self.page.get_by_label(text)

    def get_by_placeholder(self, text: str) -> Locator:
        """
        Get element by placeholder text.

        Args:
            text: Placeholder text

        Returns:
            Locator: Playwright locator instance

        Example:
            >>> search = page.get_by_placeholder("Search...")
        """
        return self.page.get_by_placeholder(text)

    def get_by_test_id(self, test_id: str) -> Locator:
        """
        Get element by test ID (data-testid attribute).

        Args:
            test_id: Test ID value

        Returns:
            Locator: Playwright locator instance

        Example:
            >>> submit = page.get_by_test_id("submit-button")
        """
        return self.page.get_by_test_id(test_id)

    # ========================================================================
    # Element Interaction Methods
    # ========================================================================

    async def click(self, selector: str, **kwargs: Any) -> None:
        """
        Click an element.

        Args:
            selector: Element selector
            **kwargs: Additional click options (force, timeout, etc.)

        Example:
            >>> await page.click("#submit-button")
            >>> await page.click("button", force=True)
        """
        logger.debug(f"Clicking element: {selector}")
        await self.page.click(selector, **kwargs)

    async def fill(self, selector: str, value: str, **kwargs: Any) -> None:
        """
        Fill an input field.

        Args:
            selector: Element selector
            value: Value to fill
            **kwargs: Additional fill options

        Example:
            >>> await page.fill("#email", "user@test.com")
        """
        logger.debug(f"Filling '{selector}' with: {value}")
        await self.page.fill(selector, value, **kwargs)

    async def type(self, selector: str, text: str, delay: int = 50) -> None:
        """
        Type text character by character (simulates real typing).

        Args:
            selector: Element selector
            text: Text to type
            delay: Delay between keystrokes in milliseconds

        Example:
            >>> await page.type("#search", "test query", delay=100)
        """
        logger.debug(f"Typing into '{selector}': {text}")
        await self.page.type(selector, text, delay=delay)

    async def select_option(self, selector: str, value: str | list[str], **kwargs: Any) -> None:
        """
        Select option(s) from a dropdown.

        Args:
            selector: Select element selector
            value: Value(s) to select
            **kwargs: Additional select options

        Example:
            >>> await page.select_option("#country", "US")
            >>> await page.select_option("#colors", ["red", "blue"])
        """
        logger.debug(f"Selecting '{value}' from '{selector}'")
        await self.page.select_option(selector, value, **kwargs)

    async def check(self, selector: str) -> None:
        """
        Check a checkbox or radio button.

        Args:
            selector: Element selector

        Example:
            >>> await page.check("#agree-terms")
        """
        logger.debug(f"Checking: {selector}")
        await self.page.check(selector)

    async def uncheck(self, selector: str) -> None:
        """
        Uncheck a checkbox.

        Args:
            selector: Element selector

        Example:
            >>> await page.uncheck("#newsletter")
        """
        logger.debug(f"Unchecking: {selector}")
        await self.page.uncheck(selector)

    async def hover(self, selector: str) -> None:
        """
        Hover over an element.

        Args:
            selector: Element selector

        Example:
            >>> await page.hover("#dropdown-menu")
        """
        logger.debug(f"Hovering over: {selector}")
        await self.page.hover(selector)

    async def scroll_to(self, selector: str) -> None:
        """
        Scroll to an element.

        Args:
            selector: Element selector

        Example:
            >>> await page.scroll_to("#footer")
        """
        logger.debug(f"Scrolling to: {selector}")
        await self.locator(selector).scroll_into_view_if_needed()

    # ========================================================================
    # Wait Methods
    # ========================================================================

    async def wait_for_selector(
        self,
        selector: str,
        state: str = "visible",
        timeout: int | None = None,
    ) -> None:
        """
        Wait for element to reach specified state.

        Args:
            selector: Element selector
            state: Element state (visible, hidden, attached, detached)
            timeout: Maximum wait time in milliseconds

        Example:
            >>> await page.wait_for_selector("#success-message", state="visible")
        """
        logger.debug(f"Waiting for '{selector}' to be {state}")
        await self.page.wait_for_selector(
            selector,
            state=state,  # type: ignore
            timeout=timeout or self.timeout,
        )

    async def wait_for_url(self, url: str, timeout: int | None = None) -> None:
        """
        Wait for URL to match the specified pattern.

        Args:
            url: URL or URL pattern to wait for
            timeout: Maximum wait time in milliseconds

        Example:
            >>> await page.wait_for_url("**/dashboard")
        """
        logger.debug(f"Waiting for URL: {url}")
        await self.page.wait_for_url(url, timeout=timeout or self.timeout)

    async def wait_for_timeout(self, timeout: int) -> None:
        """
        Wait for a specified time (use sparingly - prefer explicit waits).

        Args:
            timeout: Time to wait in milliseconds

        Example:
            >>> await page.wait_for_timeout(1000)  # Wait 1 second
        """
        logger.debug(f"Waiting for {timeout}ms")
        await self.page.wait_for_timeout(timeout)

    # ========================================================================
    # Assertion Helpers
    # ========================================================================

    async def assert_element_visible(self, selector: str) -> None:
        """
        Assert that an element is visible.

        Args:
            selector: Element selector

        Example:
            >>> await page.assert_element_visible("#success-message")
        """
        await expect(self.locator(selector)).to_be_visible()
        logger.debug(f"Verified '{selector}' is visible")

    async def assert_element_hidden(self, selector: str) -> None:
        """
        Assert that an element is hidden.

        Args:
            selector: Element selector

        Example:
            >>> await page.assert_element_hidden("#loading-spinner")
        """
        await expect(self.locator(selector)).to_be_hidden()
        logger.debug(f"Verified '{selector}' is hidden")

    async def assert_text_content(self, selector: str, expected_text: str) -> None:
        """
        Assert that an element contains expected text.

        Args:
            selector: Element selector
            expected_text: Expected text content

        Example:
            >>> await page.assert_text_content("h1", "Welcome")
        """
        await expect(self.locator(selector)).to_contain_text(expected_text)
        logger.debug(f"Verified '{selector}' contains text: {expected_text}")

    async def assert_url_contains(self, url_part: str) -> None:
        """
        Assert that current URL contains specified text.

        Args:
            url_part: Text that should be in the URL

        Example:
            >>> await page.assert_url_contains("/dashboard")
        """
        await expect(self.page).to_have_url(url_part)
        logger.debug(f"Verified URL contains: {url_part}")

    # ========================================================================
    # Information Retrieval Methods
    # ========================================================================

    async def get_text(self, selector: str) -> str:
        """
        Get text content of an element.

        Args:
            selector: Element selector

        Returns:
            str: Element text content

        Example:
            >>> text = await page.get_text("h1")
        """
        element = self.locator(selector)
        text = await element.text_content()
        return (text or "").strip()

    async def get_attribute(self, selector: str, attribute: str) -> str | None:
        """
        Get attribute value of an element.

        Args:
            selector: Element selector
            attribute: Attribute name

        Returns:
            str | None: Attribute value

        Example:
            >>> href = await page.get_attribute("a", "href")
        """
        return await self.locator(selector).get_attribute(attribute)

    async def get_elements_count(self, selector: str) -> int:
        """
        Get count of elements matching selector.

        Args:
            selector: Element selector

        Returns:
            int: Number of matching elements

        Example:
            >>> count = await page.get_elements_count(".product-item")
        """
        return await self.locator(selector).count()

    async def is_visible(self, selector: str) -> bool:
        """
        Check if an element is visible.

        Args:
            selector: Element selector

        Returns:
            bool: True if visible

        Example:
            >>> if await page.is_visible("#error"):
            >>>     print("Error is displayed")
        """
        try:
            return await self.locator(selector).is_visible()
        except Exception:
            return False

    async def is_enabled(self, selector: str) -> bool:
        """
        Check if an element is enabled.

        Args:
            selector: Element selector

        Returns:
            bool: True if enabled

        Example:
            >>> if await page.is_enabled("#submit"):
            >>>     await page.click("#submit")
        """
        return await self.locator(selector).is_enabled()

    async def is_checked(self, selector: str) -> bool:
        """
        Check if a checkbox/radio is checked.

        Args:
            selector: Element selector

        Returns:
            bool: True if checked

        Example:
            >>> if await page.is_checked("#agree"):
            >>>     print("User agreed to terms")
        """
        return await self.locator(selector).is_checked()

    # ========================================================================
    # Screenshot and Debugging
    # ========================================================================

    async def take_screenshot(self, name: str, full_page: bool = False) -> None:
        """
        Capture a screenshot of the page.

        Args:
            name: Screenshot file name
            full_page: Capture full scrollable page

        Example:
            >>> await page.take_screenshot("error_state", full_page=True)
        """
        from utils.helpers import take_screenshot

        await take_screenshot(self.page, name, full_page=full_page)

    async def highlight_element(self, selector: str, duration: int = 1000) -> None:
        """
        Highlight an element (useful for debugging).

        Args:
            selector: Element selector
            duration: Highlight duration in milliseconds

        Example:
            >>> await page.highlight_element("#important-button", duration=2000)
        """
        from utils.helpers import highlight_element

        await highlight_element(self.page, selector, duration=duration)
