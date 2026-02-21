"""
Page Helper Functions
=====================
Shared utilities for page objects: navigation, load-state waiting, and
locator convenience functions.

These exist because they handle real Playwright API quirks:
- ``get_text`` normalises the ``str | None`` that ``text_content()`` returns
- ``is_visible_safe`` catches exceptions on complex locator chains
- ``navigate_to`` / ``wait_for_load`` centralise the load-state dance
  so every page object doesn't duplicate it

Usage:
    from pages.page_helpers import navigate_to, wait_for_load, get_text

    class MyPage:
        URL = "/my-page"

        async def navigate(self) -> None:
            await navigate_to(self.page, self.URL)
"""

import logging

from playwright.async_api import Locator, Page

from config import settings

logger = logging.getLogger(__name__)


async def navigate_to(page: Page, path: str) -> None:
    """Navigate to *path* (relative to base URL) and wait for load."""
    target_url = f"{settings.base_url}{path}"
    logger.info(f"Navigating to: {target_url}")
    await page.goto(target_url, wait_until="domcontentloaded")
    await wait_for_load(page)


async def wait_for_load(page: Page, timeout: int | None = None) -> None:
    """Wait for both ``load`` and ``networkidle`` states."""
    _timeout = timeout or settings.default_timeout
    try:
        await page.wait_for_load_state("load", timeout=_timeout)
        await page.wait_for_load_state("networkidle", timeout=_timeout)
        logger.debug("Page fully loaded")
    except Exception as e:
        logger.warning(f"Page load timeout: {e}")


async def reload_page(page: Page) -> None:
    """Reload the current page and wait for load."""
    logger.info("Reloading page")
    await page.reload(wait_until="domcontentloaded")
    await wait_for_load(page)


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
