"""
============================================================================
Settings Configuration Module
============================================================================
This module defines all configuration settings for the test framework using
Pydantic for type-safe configuration with validation.

Architecture:
- Uses Pydantic Settings for environment variable loading
- Supports multiple environments (dev, staging, prod)
- Validates all configuration at startup
- Provides type-safe access to settings throughout the framework

Key Features:
- Environment-based configuration
- Automatic .env file loading
- Type validation and coercion
- Nested configuration models
- Default values with overrides

Usage:
    from config import settings

    # Access settings
    print(settings.base_url)
    print(settings.browser.headless)
    print(settings.test.default_timeout)

Author: Your Name
Created: 2026-01-23
============================================================================
"""

import os
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """
    Enumeration of supported environment types.

    This ensures type safety when specifying the environment and provides
    IDE autocomplete support.
    """

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class BrowserType(str, Enum):
    """
    Enumeration of supported browser types.

    Playwright supports these three browser engines, each with different
    characteristics and use cases.
    """

    CHROMIUM = "chromium"  # Google Chrome, Microsoft Edge
    FIREFOX = "firefox"  # Mozilla Firefox
    WEBKIT = "webkit"  # Apple Safari


class TraceMode(str, Enum):
    """
    Enumeration of Playwright trace recording modes.

    Traces provide detailed execution logs for debugging test failures.
    """

    ON = "on"  # Always record traces
    OFF = "off"  # Never record traces
    RETAIN_ON_FAILURE = "retain-on-failure"  # Keep traces only for failed tests
    ON_FIRST_RETRY = "on-first-retry"  # Record on retry attempts


class VideoMode(str, Enum):
    """
    Enumeration of video recording modes.

    Videos capture the browser screen during test execution.
    """

    ON = "on"  # Always record videos
    OFF = "off"  # Never record videos
    RETAIN_ON_FAILURE = "retain-on-failure"  # Keep videos only for failed tests
    ON_FIRST_RETRY = "on-first-retry"  # Record on retry attempts


class BrowserConfig(BaseSettings):
    """
    Browser-specific configuration settings.

    This class encapsulates all browser-related settings including
    browser type, viewport size, headless mode, and performance options.

    Attributes:
        browser: Browser engine to use (chromium/firefox/webkit)
        headless: Whether to run browser in headless mode
        viewport_width: Browser viewport width in pixels
        viewport_height: Browser viewport height in pixels
        slow_mo: Milliseconds to slow down Playwright operations (for debugging)
        ignore_https_errors: Whether to ignore HTTPS certificate errors
        device_name: Device to emulate (for mobile testing)
        mobile_emulation: Whether to enable mobile device emulation
    """

    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False)

    browser: BrowserType = Field(
        default=BrowserType.CHROMIUM,
        description="Browser engine to use for testing",
    )

    headless: bool = Field(
        default=True,
        description="Run browser in headless mode (no visible UI)",
    )

    viewport_width: int = Field(
        default=1920,
        ge=320,
        le=3840,
        description="Browser viewport width in pixels",
    )

    viewport_height: int = Field(
        default=1080,
        ge=240,
        le=2160,
        description="Browser viewport height in pixels",
    )

    slow_mo: int = Field(
        default=0,
        ge=0,
        le=5000,
        description="Milliseconds to slow down operations (debugging)",
    )

    ignore_https_errors: bool = Field(
        default=False,
        description="Ignore HTTPS certificate errors",
    )

    device_name: str | None = Field(
        default=None,
        description="Device to emulate (e.g., 'iPhone 13', 'Pixel 5')",
    )

    mobile_emulation: bool = Field(
        default=False,
        description="Enable mobile device emulation",
    )

    user_agent: str | None = Field(
        default=None,
        description="Custom user agent string",
    )

    accept_downloads: bool = Field(
        default=True,
        description="Enable file downloads",
    )

    downloads_dir: str = Field(
        default="downloads",
        description="Directory for downloaded files",
    )


class TestConfig(BaseSettings):
    """
    Test execution configuration settings.

    This class defines settings related to test execution behavior,
    timeouts, retries, and parallel execution.

    Attributes:
        page_load_timeout: Maximum time to wait for page load (ms)
        default_timeout: Default timeout for assertions and waits (ms)
        workers: Number of parallel workers for test execution
        max_failures: Maximum number of test failures before stopping
        retries: Number of times to retry failed tests
        screenshot_on_failure: Capture screenshot when test fails
    """

    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False)

    page_load_timeout: int = Field(
        default=30000,
        ge=5000,
        le=120000,
        description="Maximum time to wait for page load (milliseconds)",
    )

    default_timeout: int = Field(
        default=30000,
        ge=5000,
        le=120000,
        description="Default timeout for assertions and waits (milliseconds)",
    )

    workers: int = Field(
        default=4,
        ge=1,
        le=16,
        description="Number of parallel workers for test execution",
    )

    max_failures: int = Field(
        default=1,
        ge=0,
        description="Maximum number of test failures before stopping",
    )

    retries: int = Field(
        default=1,
        ge=0,
        le=5,
        description="Number of times to retry failed tests",
    )

    screenshot_on_failure: bool = Field(
        default=True,
        description="Capture screenshot when test fails",
    )

    trace_mode: TraceMode = Field(
        default=TraceMode.RETAIN_ON_FAILURE,
        description="Playwright trace recording mode",
    )

    video_mode: VideoMode = Field(
        default=VideoMode.RETAIN_ON_FAILURE,
        description="Video recording mode",
    )


class Settings(BaseSettings):
    """
    Main settings class that aggregates all configuration.

    This is the primary interface for accessing framework configuration.
    It loads settings from environment variables and .env files, with
    support for environment-specific base URLs and credentials.

    The class uses Pydantic Settings to automatically load and validate
    configuration from multiple sources in this order:
    1. Environment variables
    2. .env file
    3. Default values

    Attributes:
        env: Current environment (development/staging/production)
        base_url: Base URL for the application under test
        standard_user: Username for standard test user
        standard_password: Password for standard test user
        locked_out_user: Username for locked out user (negative testing)
        problem_user: Username for problem user
        performance_glitch_user: Username for performance testing
        default_password: Default password for all test users
        browser: Browser configuration settings
        test: Test execution configuration settings
        log_level: Logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        log_to_console: Enable console logging
        log_to_file: Enable file logging
        log_file_path: Path to log file
        enable_html_report: Generate HTML test report
        enable_allure_report: Generate Allure test report
        report_dir: Directory for test reports
        ci: Running in CI/CD pipeline
        ci_platform: CI/CD platform name
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment Configuration
    env: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Current environment (development/staging/production)",
    )

    # Base URLs for different environments
    base_url_dev: str = Field(
        default="https://www.saucedemo.com",
        description="Base URL for development environment",
    )

    base_url_staging: str = Field(
        default="https://www.saucedemo.com",
        description="Base URL for staging environment",
    )

    base_url_prod: str = Field(
        default="https://www.saucedemo.com",
        description="Base URL for production environment",
    )

    # Test User Credentials
    standard_user: str = Field(
        default="standard_user",
        description="Username for standard test user",
    )

    standard_password: str = Field(
        default="secret_sauce",
        description="Password for standard test user",
    )

    locked_out_user: str = Field(
        default="locked_out_user",
        description="Username for locked out user (negative testing)",
    )

    problem_user: str = Field(
        default="problem_user",
        description="Username for problem user",
    )

    performance_glitch_user: str = Field(
        default="performance_glitch_user",
        description="Username for performance glitch user",
    )

    error_user: str = Field(
        default="error_user",
        description="Username for error user",
    )

    visual_user: str = Field(
        default="visual_user",
        description="Username for visual user",
    )

    default_password: str = Field(
        default="secret_sauce",
        description="Default password for all test users",
    )

    # Flat Browser Configuration Fields
    browser: BrowserConfig | str | BrowserType = Field(
        default="chromium",
        description="Browser engine to use for testing",
    )

    headless: bool = Field(
        default=True,
        description="Run browser in headless mode (no visible UI)",
    )

    viewport_width: int = Field(
        default=1920,
        ge=320,
        le=3840,
        description="Browser viewport width in pixels",
    )

    viewport_height: int = Field(
        default=1080,
        ge=240,
        le=2160,
        description="Browser viewport height in pixels",
    )

    slow_mo: int = Field(
        default=0,
        ge=0,
        le=5000,
        description="Milliseconds to slow down operations (debugging)",
    )

    ignore_https_errors: bool = Field(
        default=False,
        description="Ignore HTTPS certificate errors",
    )

    device_name: str | None = Field(
        default=None,
        description="Device to emulate (e.g., 'iPhone 13', 'Pixel 5')",
    )

    mobile_emulation: bool = Field(
        default=False,
        description="Enable mobile device emulation",
    )

    user_agent: str | None = Field(
        default=None,
        description="Custom user agent string",
    )

    accept_downloads: bool = Field(
        default=True,
        description="Enable file downloads",
    )

    downloads_dir: str = Field(
        default="downloads",
        description="Directory for downloaded files",
    )

    # Flat Test Configuration Fields
    page_load_timeout: int = Field(
        default=30000,
        ge=5000,
        le=120000,
        description="Maximum time to wait for page load (milliseconds)",
    )

    default_timeout: int = Field(
        default=30000,
        ge=5000,
        le=120000,
        description="Default timeout for assertions and waits (milliseconds)",
    )

    workers: int = Field(
        default=4,
        ge=1,
        le=16,
        description="Number of parallel workers for test execution",
    )

    max_failures: int = Field(
        default=1,
        ge=0,
        description="Maximum number of test failures before stopping",
    )

    retries: int = Field(
        default=1,
        ge=0,
        le=5,
        description="Number of times to retry failed tests",
    )

    screenshot_on_failure: bool = Field(
        default=True,
        description="Capture screenshot when test fails",
    )

    trace_mode: TraceMode | str = Field(
        default="retain-on-failure",
        description="Playwright trace recording mode",
    )

    video_mode: VideoMode | str = Field(
        default="retain-on-failure",
        description="Video recording mode",
    )

    # Nested Configuration Objects (will be initialized in validators)
    browser_obj: BrowserConfig | None = Field(
        default=None,
        exclude=True,
    )

    test_obj: TestConfig | None = Field(
        default=None,
        exclude=True,
    )

    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL)",
    )

    log_to_console: bool = Field(
        default=True,
        description="Enable console logging",
    )

    log_to_file: bool = Field(
        default=True,
        description="Enable file logging",
    )

    log_file_path: str = Field(
        default="logs/test_execution.log",
        description="Path to log file",
    )

    # Reporting Configuration
    enable_html_report: bool = Field(
        default=True,
        description="Generate HTML test report",
    )

    enable_allure_report: bool = Field(
        default=True,
        description="Generate Allure test report",
    )

    report_dir: str = Field(
        default="reports",
        description="Directory for test reports",
    )

    # CI/CD Configuration
    ci: bool = Field(
        default=False,
        description="Running in CI/CD pipeline",
    )

    ci_platform: str = Field(
        default="local",
        description="CI/CD platform (gitlab/github/jenkins/local)",
    )

    # API Testing Configuration
    api_base_url: str = Field(
        default="https://www.saucedemo.com",
        description="Base URL for API testing",
    )

    api_timeout: int = Field(
        default=10000,
        ge=1000,
        le=60000,
        description="API request timeout (milliseconds)",
    )

    @property
    def base_url(self) -> str:
        """
        Get the base URL for the current environment.

        This property dynamically returns the appropriate base URL based on
        the current environment setting.

        Returns:
            str: Base URL for the current environment

        Example:
            >>> settings.env = Environment.DEVELOPMENT
            >>> print(settings.base_url)
            'https://www.saucedemo.com'
        """
        env_to_url = {
            Environment.DEVELOPMENT: self.base_url_dev,
            Environment.STAGING: self.base_url_staging,
            Environment.PRODUCTION: self.base_url_prod,
        }
        return env_to_url.get(self.env, self.base_url_dev)

    @property
    def project_root(self) -> Path:
        """
        Get the project root directory.

        Returns:
            Path: Absolute path to project root directory

        Example:
            >>> root = settings.project_root
            >>> print(root / "tests")
            /path/to/project/tests
        """
        return Path(__file__).parent.parent

    @property
    def reports_dir(self) -> Path:
        """
        Get the full path to the reports directory.

        Returns:
            Path: Absolute path to reports directory
        """
        return self.project_root / self.report_dir

    @property
    def logs_dir(self) -> Path:
        """
        Get the full path to the logs directory.

        Returns:
            Path: Absolute path to logs directory
        """
        log_path = Path(self.log_file_path)
        return self.project_root / log_path.parent

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """
        Validate that the log level is one of the allowed values.

        Args:
            v: Log level string to validate

        Returns:
            str: Validated and uppercased log level

        Raises:
            ValueError: If log level is not valid
        """
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v_upper

    @model_validator(mode="after")
    def initialize_nested_configs(self) -> "Settings":
        """
        Initialize nested configuration objects after model validation.
        """
        # Convert browser string to BrowserType enum if needed
        browser_val = self.browser
        if isinstance(browser_val, str):
            browser_val = BrowserType(browser_val)
        elif isinstance(browser_val, BrowserConfig):
            browser_val = browser_val.browser
        
        # Convert trace_mode and video_mode if needed
        trace_val = self.trace_mode
        if isinstance(trace_val, str):
            trace_val = TraceMode(trace_val)
        
        video_val = self.video_mode
        if isinstance(video_val, str):
            video_val = VideoMode(video_val)
        
        # Create BrowserConfig - note: we don't assign to self.browser
        # We keep the browser field as a string and use browser_obj property
        self.browser_obj = BrowserConfig(
            browser=browser_val,
            headless=self.headless,
            viewport_width=self.viewport_width,
            viewport_height=self.viewport_height,
            slow_mo=self.slow_mo,
            device_name=self.device_name,
            mobile_emulation=self.mobile_emulation,
            user_agent=self.user_agent,
            accept_downloads=self.accept_downloads,
            downloads_dir=self.downloads_dir,
            ignore_https_errors=self.ignore_https_errors,
        )
        
        # Create TestConfig
        self.test_obj = TestConfig(
            page_load_timeout=self.page_load_timeout,
            default_timeout=self.default_timeout,
            workers=self.workers,
            max_failures=self.max_failures,
            retries=self.retries,
            screenshot_on_failure=self.screenshot_on_failure,
            trace_mode=trace_val,
            video_mode=video_val,
        )
        
        return self
    
    @property
    def browser_config(self) -> BrowserConfig:
        """Get the browser configuration object."""
        if self.browser_obj is None:
            self.browser_obj = BrowserConfig()
        return self.browser_obj
    
    @property
    def test_config(self) -> TestConfig:
        """Get the test configuration object."""
        if self.test_obj is None:
            self.test_obj = TestConfig()
        return self.test_obj
    
    def __getattr__(self, name: str) -> Any:
        """
        Override __getattr__ to handle browser and test attribute access.
        This allows settings.browser and settings.test to return the config objects.
        """
        if name == 'browser':
            return self.browser_config
        elif name == 'test':
            return self.test_config
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    def __getattribute__(self, name: str) -> Any:
        """
        Override __getattribute__ to intercept browser and test access.
        """
        if name == 'browser':
            return super().__getattribute__('browser_config')
        elif name == 'test':
            return super().__getattribute__('test_config')
        return super().__getattribute__(name)

    def model_post_init(self, __context: Any) -> None:
        """
        Post-initialization hook to create required directories.

        This method is called after the model is initialized. It ensures
        that necessary directories (logs, reports, downloads) exist.

        Args:
            __context: Pydantic context (unused)
        """
        # Create logs directory
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Create reports directory
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Create downloads directory
        downloads_path = self.project_root / self.browser_config.downloads_dir
        downloads_path.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """
    Get the singleton Settings instance.

    This function uses LRU cache to ensure we only create one Settings
    instance throughout the application lifecycle. This improves performance
    and ensures consistent configuration.

    Returns:
        Settings: Singleton settings instance

    Example:
        >>> from config import get_settings
        >>> settings = get_settings()
        >>> print(settings.base_url)
        'https://www.saucedemo.com'
    """
    return Settings()


# Global settings instance for convenient access
settings = get_settings()


if __name__ == "__main__":
    """
    Module test/demonstration code.

    Run this module directly to see the current configuration:
        python -m config.settings
    """
    print("=" * 80)
    print("Current Configuration")
    print("=" * 80)
    print(f"Environment: {settings.env}")
    print(f"Base URL: {settings.base_url}")
    print(f"Browser: {settings.browser.browser}")
    print(f"Headless: {settings.browser.headless}")
    print(f"Viewport: {settings.browser.viewport_width}x{settings.browser.viewport_height}")
    print(f"Workers: {settings.test.workers}")
    print(f"Default Timeout: {settings.test.default_timeout}ms")
    print(f"Log Level: {settings.log_level}")
    print(f"CI Mode: {settings.ci}")
    print("=" * 80)
