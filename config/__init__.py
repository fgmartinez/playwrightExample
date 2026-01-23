"""
============================================================================
Config Module
============================================================================
This module provides centralized configuration management for the test
framework, including environment-specific settings, credentials, and
browser configurations.

Key Components:
- Settings: Pydantic-based configuration with validation
- Environment loaders: Load settings from .env files
- Configuration classes: Type-safe access to all settings

Usage:
    from config import settings

    # Access configuration values
    base_url = settings.base_url
    browser = settings.browser
    headless = settings.headless

Author: Your Name
Created: 2026-01-23
============================================================================
"""

from config.settings import BrowserConfig, TestConfig, get_settings, settings

__all__ = [
    "settings",
    "get_settings",
    "BrowserConfig",
    "TestConfig",
]
