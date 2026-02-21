"""
Helper Utilities
================
Utility functions used across the test framework.

Only functions that are actually imported by tests or page objects live here.
Playwright's own API handles waiting, scrolling, and element queries natively
— we don't re-wrap those.
"""

import logging
import re
from datetime import datetime
from pathlib import Path

from faker import Faker
from playwright.async_api import Page

from config import settings

logger = logging.getLogger(__name__)

faker = Faker()


async def take_screenshot(page: Page, name: str, full_page: bool = False) -> Path | None:
    """Capture a screenshot and save it to reports/screenshots/."""
    try:
        screenshots_dir = settings.project_root / "reports" / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = re.sub(r'[<>:"/\\|?*]', "_", f"{name}_{timestamp}.png")
        screenshot_path = screenshots_dir / filename

        await page.screenshot(path=str(screenshot_path), full_page=full_page)
        logger.info(f"Screenshot saved: {screenshot_path}")
        return screenshot_path
    except Exception as e:
        logger.error(f"Failed to capture screenshot: {e}")
        return None


def generate_test_user_data() -> dict[str, str]:
    """Generate a complete set of realistic test-user data via Faker."""
    return {
        "firstName": faker.first_name(),
        "lastName": faker.last_name(),
        "email": faker.email(),
        "phone": faker.phone_number(),
        "address": faker.street_address(),
        "city": faker.city(),
        "state": faker.state_abbr(),
        "zipCode": faker.zipcode(),
        "company": faker.company(),
    }
