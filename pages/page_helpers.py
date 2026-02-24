"""Stateless helper functions for working with Playwright Pages and Locators.

These handle real Playwright API quirks:
- ``get_text`` normalises the ``str | None`` that ``text_content()`` returns
- ``is_visible_safe`` catches exceptions on complex locator chains
- ``navigate_to`` / ``wait_for_load`` centralise the load-state dance
"""

import logging

from playwright.sync_api import Locator, Page

from config import settings

logger = logging.getLogger(__name__)


def navigate_to(page: Page, path: str) -> None:
    """Navigate to *path* (relative to base URL) and wait for load."""
    target_url = f"{settings.base_url}{path}"
    logger.info(f"Navigating to: {target_url}")
    page.goto(target_url, wait_until="domcontentloaded")
    wait_for_load(page)


def wait_for_load(page: Page, timeout: int | None = None) -> None:
    """Wait for both ``load`` and ``networkidle`` states."""
    _timeout = timeout or settings.default_timeout
    try:
        page.wait_for_load_state("load", timeout=_timeout)
        page.wait_for_load_state("networkidle", timeout=_timeout)
        logger.debug("Page fully loaded")
    except Exception as e:
        logger.warning(f"Page load timeout: {e}")


def reload_page(page: Page) -> None:
    """Reload the current page and wait for load."""
    logger.info("Reloading page")
    page.reload(wait_until="domcontentloaded")
    wait_for_load(page)


def get_text(locator: Locator) -> str:
    """Get text content from a locator, stripped of whitespace."""
    text = locator.text_content()
    return (text or "").strip()


def is_visible_safe(locator: Locator) -> bool:
    """Check locator visibility without raising if the element is absent."""
    try:
        return locator.is_visible()
    except Exception:
        return False
