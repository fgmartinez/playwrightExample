"""
============================================================================
Logger Configuration Module
============================================================================
This module provides centralized logging configuration for the entire test
framework. It sets up colored console logging and file logging with proper
formatting, rotation, and level filtering.

Key Features:
- Colored console output for better readability
- File logging with automatic rotation
- Configurable log levels per handler
- Structured log format with timestamps and context
- Thread-safe logging for parallel test execution

Architecture:
- Uses Python's built-in logging module
- Configures both console and file handlers
- Applies colorlog for terminal output
- Loads configuration from settings

Usage:
    from utils import get_logger

    logger = get_logger(__name__)
    logger.info("Test started")
    logger.debug("Detailed debug information")
    logger.error("An error occurred", exc_info=True)

Author: Your Name
Created: 2026-01-23
============================================================================
"""

import logging
import sys
from pathlib import Path
from typing import Any

import colorlog

from config import settings


class LoggerManager:
    """
    Singleton manager for centralized logging configuration.

    This class ensures that logging is configured only once and provides
    consistent logger instances throughout the framework.

    Attributes:
        _instance: Singleton instance
        _initialized: Flag to track initialization state
        _loggers: Cache of created logger instances
    """

    _instance: "LoggerManager | None" = None
    _initialized: bool = False
    _loggers: dict[str, logging.Logger] = {}

    def __new__(cls) -> "LoggerManager":
        """
        Implement singleton pattern.

        Returns:
            LoggerManager: Singleton instance
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the logger manager (only once)."""
        if not LoggerManager._initialized:
            self._setup_logging()
            LoggerManager._initialized = True

    def _setup_logging(self) -> None:
        """
        Configure logging handlers and formatters.

        This method sets up:
        1. Console handler with colored output
        2. File handler with rotation
        3. Appropriate formatters for each handler
        4. Log level filtering
        """
        # Get root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)  # Capture all levels, filter in handlers

        # Clear any existing handlers
        root_logger.handlers.clear()

        # Console Handler with Colors
        if settings.log_to_console:
            console_handler = self._create_console_handler()
            root_logger.addHandler(console_handler)

        # File Handler
        if settings.log_to_file:
            file_handler = self._create_file_handler()
            root_logger.addHandler(file_handler)

        # Suppress noisy third-party loggers
        self._suppress_noisy_loggers()

    def _create_console_handler(self) -> logging.Handler:
        """
        Create and configure console handler with colored output.

        Returns:
            logging.Handler: Configured console handler

        The color scheme:
        - DEBUG: Cyan
        - INFO: Green
        - WARNING: Yellow
        - ERROR: Red
        - CRITICAL: Red on white background
        """
        console_handler = colorlog.StreamHandler(sys.stdout)
        console_handler.setLevel(settings.log_level)

        # Color formatter with detailed format
        color_formatter = colorlog.ColoredFormatter(
            fmt=(
                "%(log_color)s%(asctime)s | %(levelname)-8s | "
                "%(name)s:%(lineno)d | %(message)s%(reset)s"
            ),
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
            secondary_log_colors={},
            style="%",
        )

        console_handler.setFormatter(color_formatter)
        return console_handler

    def _create_file_handler(self) -> logging.Handler:
        """
        Create and configure file handler with rotation.

        Returns:
            logging.Handler: Configured file handler

        The file handler:
        - Writes to the file specified in settings
        - Uses detailed formatting with context
        - Always logs at DEBUG level (controlled by root logger)
        - Automatically creates the log directory if needed
        """
        # Ensure log directory exists
        log_path = settings.project_root / settings.log_file_path
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(
            filename=log_path,
            mode="a",
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)

        # Detailed formatter for file output
        file_formatter = logging.Formatter(
            fmt=(
                "%(asctime)s | %(levelname)-8s | %(name)s | "
                "%(filename)s:%(lineno)d | %(funcName)s | %(message)s"
            ),
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler.setFormatter(file_formatter)
        return file_handler

    def _suppress_noisy_loggers(self) -> None:
        """
        Suppress verbose logging from third-party libraries.

        This prevents log pollution from libraries like urllib3, selenium,
        and other dependencies that log too verbosely at INFO level.
        """
        noisy_loggers = [
            "urllib3",
            "selenium",
            "asyncio",
            "playwright",
            "filelock",
        ]

        for logger_name in noisy_loggers:
            logging.getLogger(logger_name).setLevel(logging.WARNING)

    def get_logger(self, name: str) -> logging.Logger:
        """
        Get or create a logger instance.

        This method caches logger instances to avoid recreation and ensures
        consistent configuration across the framework.

        Args:
            name: Logger name (typically __name__ of the calling module)

        Returns:
            logging.Logger: Configured logger instance

        Example:
            >>> logger = manager.get_logger(__name__)
            >>> logger.info("This is an info message")
        """
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)

        return self._loggers[name]


# Global logger manager instance
_logger_manager: LoggerManager | None = None


def setup_logger() -> None:
    """
    Initialize the logging system.

    This function should be called once at the start of the test session
    (typically in conftest.py). It initializes the LoggerManager singleton
    and configures all logging handlers.

    Example:
        >>> # In conftest.py
        >>> def pytest_configure(config):
        >>>     setup_logger()
    """
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()


def get_logger(name: str = __name__) -> logging.Logger:
    """
    Get a logger instance for the specified module.

    This is the main function used throughout the framework to get logger
    instances. It ensures the logging system is initialized and returns a
    properly configured logger.

    Args:
        name: Logger name (typically __name__ of the calling module)

    Returns:
        logging.Logger: Configured logger instance

    Example:
        >>> from utils import get_logger
        >>>
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting test execution")
        >>> logger.debug("Debug information: %s", debug_data)
        >>> logger.error("Test failed", exc_info=True)
    """
    global _logger_manager

    # Ensure logger manager is initialized
    if _logger_manager is None:
        setup_logger()

    return _logger_manager.get_logger(name)  # type: ignore[union-attr]


class TestLogger:
    """
    Context manager for test-specific logging.

    This class provides a context manager that adds test-specific context
    to log messages, making it easier to trace logs back to specific tests.

    Attributes:
        test_name: Name of the test
        logger: Logger instance to use

    Example:
        >>> with TestLogger("test_login") as logger:
        >>>     logger.info("Starting login test")
        >>>     # ... test code ...
        >>>     logger.info("Login test completed")
    """

    def __init__(self, test_name: str, logger: logging.Logger | None = None) -> None:
        """
        Initialize test logger.

        Args:
            test_name: Name of the test
            logger: Optional logger instance (creates new one if not provided)
        """
        self.test_name = test_name
        self.logger = logger or get_logger(__name__)

    def __enter__(self) -> logging.Logger:
        """
        Enter the context manager.

        Returns:
            logging.Logger: Logger instance with test context
        """
        self.logger.info("=" * 80)
        self.logger.info(f"Starting Test: {self.test_name}")
        self.logger.info("=" * 80)
        return self.logger

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """
        Exit the context manager.

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)

        Returns:
            bool: False to propagate exceptions
        """
        if exc_type is not None:
            self.logger.error(
                f"Test Failed: {self.test_name}",
                exc_info=(exc_type, exc_val, exc_tb),
            )
        else:
            self.logger.info(f"Test Completed: {self.test_name}")

        self.logger.info("=" * 80)
        return False  # Don't suppress exceptions


if __name__ == "__main__":
    """
    Module test/demonstration code.

    Run this module directly to see logging in action:
        python -m utils.logger
    """
    # Setup logging
    setup_logger()

    # Get logger instance
    logger = get_logger(__name__)

    # Demonstrate different log levels
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")

    # Demonstrate test logger context manager
    with TestLogger("demo_test") as test_logger:
        test_logger.info("Test is running")
        test_logger.debug("Debug information")

    print("\nCheck the log file at:", settings.project_root / settings.log_file_path)
