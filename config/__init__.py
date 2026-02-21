"""
Config Module
=============
Usage:
    from config import settings

    base_url = settings.base_url
    headless = settings.headless
"""

from config.settings import Settings, get_settings, settings

__all__ = ["Settings", "get_settings", "settings"]
