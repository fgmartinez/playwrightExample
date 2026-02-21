"""
Page Navigator and Locator Utilities
=====================================
Provides PageNavigator for navigation concerns and two standalone helper
functions for locator interactions. Used by page objects via composition
instead of inheritance.

Usage:
    class MyPage:
        URL = "/my-page"

        def __init__(self, page: Page) -> None:
            self.page = page
            self._nav = PageNavigator(page, settings.test.default_timeout)

        async def navigate(self) -> None:
            await self._nav.go(self.URL)
"""

from playwright.async_api import Locator, Page

import logging

from config import settings

logger = logging.getLogger(__name__)


class PageNavigator:
    """Handles page navigation and load-state waiting for a page object."""

    def __init__(self, page: Page, timeout: int) -> None:
        self._page = page
        self._timeout = timeout

    async def go(self, path: str) -> None:
        """Navigate to a path relative to the base URL."""
        target_url = f"{settings.base_url}{path}"
        logger.info(f"Navigating to: {target_url}")
        await self._page.goto(target_url, wait_until="domcontentloaded")
        await self.wait_for_load()

    async def wait_for_load(self) -> None:
        """Wait for the page load and networkidle states."""
        try:
            await self._page.wait_for_load_state("load", timeout=self._timeout)
            await self._page.wait_for_load_state("networkidle", timeout=self._timeout)
            logger.debug("Page fully loaded")
        except Exception as e:
            logger.warning(f"Page load timeout: {e}")

    async def reload(self) -> None:
        """Reload the current page and wait for load."""
        logger.info("Reloading page")
        await self._page.reload(wait_until="domcontentloaded")
        await self.wait_for_load()


async def get_text(locator: Locator) -> str:
    """Get text content from a locator, stripped of whitespace."""
    text = await locator.text_content()
    return (text or "").strip()


async def is_visible_safe(locator: Locator) -> bool:
    """Check locator visibility without raising if the element is absent."""
    try:
        return await locator.is_visible()
    except Exception:
        return False
