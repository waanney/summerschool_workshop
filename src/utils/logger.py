"""
Logging configuration and utilities module.

This module provides centralized logging configuration for the summerschool
workshop project. It supports both file and console logging with configurable
log levels and formatters.
"""

import logging
from typing import Optional
from enum import Enum
from pathlib import Path


class LogLevel(str, Enum):
    """Enum for log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(str, Enum):
    """Enum for log formats."""

    SIMPLE = "simple"
    DETAILED = "detailed"
    JSON = "json"


def setup_logger(
    log_file: str = "app.log",
    log_level: LogLevel = LogLevel.INFO,
    console_level: LogLevel = LogLevel.INFO,
    file_level: LogLevel = LogLevel.ERROR,
    log_format: LogFormat = LogFormat.SIMPLE,
) -> logging.Logger:
    """
    Configure the logging system with file and console handlers.

    This function sets up a comprehensive logging system that writes logs
    to both a file and the console. It supports different log levels for
    each output destination and various formatting options.

    Args:
        log_file: Path to the log file (default: "app.log")
        log_level: Overall log level for the logger (default: INFO)
        console_level: Log level for console output (default: INFO)
        file_level: Log level for file output (default: ERROR)
        log_format: Format style for log messages (default: SIMPLE)

    Returns:
        logging.Logger: Configured logger instance

    Raises:
        PermissionError: If unable to write to the log file
        ValueError: If invalid log levels are provided

    Example:
        >>> logger = setup_logger("my_app.log", LogLevel.DEBUG)
        >>> logger.info("Application started")
    """
    logger: logging.Logger = logging.getLogger(__name__)
    logger.setLevel(_get_log_level(log_level))

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter: logging.Formatter = _create_formatter(log_format)

    # Log to file
    file_handler: logging.FileHandler = _create_file_handler(
        log_file, file_level, formatter
    )
    logger.addHandler(file_handler)

    # Log to console
    console_handler: logging.StreamHandler = _create_console_handler(
        console_level, formatter
    )
    logger.addHandler(console_handler)

    return logger


def _get_log_level(log_level: LogLevel) -> int:
    """
    Convert LogLevel enum to logging module level.

    Args:
        log_level: LogLevel enum value

    Returns:
        int: Corresponding logging module level constant
    """
    level_mapping: dict[LogLevel, int] = {
        LogLevel.DEBUG: logging.DEBUG,
        LogLevel.INFO: logging.INFO,
        LogLevel.WARNING: logging.WARNING,
        LogLevel.ERROR: logging.ERROR,
        LogLevel.CRITICAL: logging.CRITICAL,
    }
    return level_mapping.get(log_level, logging.INFO)


def _create_formatter(log_format: LogFormat) -> logging.Formatter:
    """
    Create a log formatter based on the specified format.

    Args:
        log_format: Format style for log messages

    Returns:
        logging.Formatter: Configured formatter instance
    """
    if log_format == LogFormat.SIMPLE:
        return logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    elif log_format == LogFormat.DETAILED:
        return logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )
    elif log_format == LogFormat.JSON:
        return logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
        )
    else:
        return logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")


def _create_file_handler(
    log_file: str, file_level: LogLevel, formatter: logging.Formatter
) -> logging.FileHandler:
    """
    Create a file handler for logging.

    Args:
        log_file: Path to the log file
        file_level: Log level for file output
        formatter: Formatter to use for log messages

    Returns:
        logging.FileHandler: Configured file handler

    Raises:
        PermissionError: If unable to write to the log file
    """
    # Ensure log directory exists
    log_path: Path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler: logging.FileHandler = logging.FileHandler(log_file)
    file_handler.setLevel(_get_log_level(file_level))
    file_handler.setFormatter(formatter)
    return file_handler


def _create_console_handler(
    console_level: LogLevel, formatter: logging.Formatter
) -> logging.StreamHandler:
    """
    Create a console handler for logging.

    Args:
        console_level: Log level for console output
        formatter: Formatter to use for log messages

    Returns:
        logging.StreamHandler: Configured console handler
    """
    console_handler: logging.StreamHandler = logging.StreamHandler()
    console_handler.setLevel(_get_log_level(console_level))
    console_handler.setFormatter(formatter)
    return console_handler


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    This function provides a convenient way to get a logger that uses
    the default configuration. If no logger has been set up yet, it
    will create one with default settings.

    Args:
        name: Name for the logger (default: None, uses module name)

    Returns:
        logging.Logger: Logger instance
    """
    if name is None:
        name = __name__

    logger: logging.Logger = logging.getLogger(name)

    # If no handlers are configured, set up default logging
    if not logger.handlers:
        setup_logger()

    return logger
