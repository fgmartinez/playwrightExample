"""
Pytest Configuration and Global Fixtures
=========================================
Root conftest providing browser configuration, logging hooks, and
shared fixtures.  Only fixtures that are actually consumed by tests
live here.
"""

from typing import Any, Generator

import pytest
from pytest import Config, Item, StashKey

from config import settings
import logging


logger = logging.getLogger(__name__)

phase_key = StashKey[dict[str, Any]]()


# ============================================================================
# Pytest Hooks
# ============================================================================


def pytest_configure(config: Config) -> None:
    """Set up coloured logging and create output directories."""
    import colorlog

    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
    )
    logging.basicConfig(handlers=[handler], level=logging.INFO)
    for noisy in ("playwright", "asyncio", "urllib3", "filelock"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logger.info("=" * 80)
    logger.info("Test Session Started")
    logger.info(f"Base URL: {settings.base_url}")
    logger.info(f"Browser: {settings.browser}  Headless: {settings.headless}")
    logger.info("=" * 80)

    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    settings.logs_dir.mkdir(parents=True, exist_ok=True)


def pytest_collection_finish(session: Any) -> None:
    logger.info(f"Collected {len(session.items)} test(s)")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: Item, call: Any) -> Generator[None, Any, None]:
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        item.stash[phase_key] = {"report": report}
        if report.passed:
            logger.info(f"PASSED: {item.nodeid}")
        elif report.failed:
            logger.error(f"FAILED: {item.nodeid}")
            logger.error(f"Error: {report.longreprtext}")
        elif report.skipped:
            logger.warning(f"SKIPPED: {item.nodeid}")


def pytest_sessionfinish(session: Any, exitstatus: int) -> None:
    logger.info("=" * 80)
    logger.info(f"Test Session Finished  (exit status {exitstatus})")
    logger.info("=" * 80)


# ============================================================================
# Browser Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def browser_type_launch_args() -> dict[str, Any]:
    """Launch arguments consumed by pytest-playwright."""
    launch_args: dict[str, Any] = {
        "headless": settings.headless,
        "slow_mo": settings.slow_mo,
    }
    if settings.browser == "chromium":
        launch_args["args"] = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
        ]
    return launch_args


@pytest.fixture(scope="session")
def browser_context_args() -> dict[str, Any]:
    """Context arguments consumed by pytest-playwright."""
    ctx: dict[str, Any] = {
        "viewport": {
            "width": settings.viewport_width,
            "height": settings.viewport_height,
        },
        "ignore_https_errors": settings.ignore_https_errors,
        "accept_downloads": settings.accept_downloads,
    }
    if settings.user_agent:
        ctx["user_agent"] = settings.user_agent
    return ctx


# ============================================================================
# Utility Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
def log_test_info(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    """Log test start/finish for every test (autouse)."""
    name = request.node.name
    logger.info(f"Starting test: {name}")
    yield
    logger.info(f"Finished test: {name}")
