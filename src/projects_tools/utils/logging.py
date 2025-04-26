"""
Logging configuration for projects_tools.

This module provides a centralized logging configuration for projects_tools.
"""

import logging
import os
import sys
from typing import Optional, Union

# Default log level
DEFAULT_LOG_LEVEL = logging.INFO

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
SIMPLE_FORMAT = "%(message)s"

# Environment variable for log level
LOG_LEVEL_ENV_VAR = "PROJECTS_TOOLS_LOG_LEVEL"


def get_log_level() -> int:
    """
    Get the log level from environment variable or use default.

    Returns:
        Log level as an integer.
    """
    log_level_str = os.environ.get(LOG_LEVEL_ENV_VAR)
    if log_level_str:
        log_level_str = log_level_str.upper()
        if log_level_str in logging._nameToLevel:
            return logging._nameToLevel[log_level_str]
        try:
            return int(log_level_str)
        except ValueError:
            pass
    return DEFAULT_LOG_LEVEL


def configure_logging(level: Optional[Union[int, str]] = None) -> None:
    """
    Configure logging for projects_tools.

    Args:
        level: Log level to use. If None, will use the level from environment
            variable or default.
    """
    if level is None:
        level = get_log_level()

    # Configure root logger
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Configure projects_tools logger
    logger = logging.getLogger("projects_tools")
    if isinstance(level, (int, str)):
        logger.setLevel(level)

    # Silence some noisy loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.

    Args:
        name: Logger name.

    Returns:
        Logger instance.
    """
    return logging.getLogger(name)


def set_log_level(level: Optional[Union[int, str]]) -> None:
    """
    Set the log level for projects_tools loggers.

    Args:
        level: Log level to set.
    """
    if level is None:
        level = get_log_level()

    # Set level for projects_tools logger
    logger = logging.getLogger("projects_tools")
    if isinstance(level, (int, str)):
        logger.setLevel(level)
