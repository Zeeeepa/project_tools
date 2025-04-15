"""
Logging utilities for projects_tools.

This module provides a centralized logging configuration for projects_tools.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Union, Dict, Any

# Default logging format
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Default logging level
DEFAULT_LEVEL = logging.INFO


def configure_logging(
    level: Optional[Union[int, str]] = None,
    format_str: Optional[str] = None,
    log_file: Optional[Union[str, Path]] = None,
    log_to_console: bool = True,
    log_to_file: bool = False,
    config: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Configure logging for projects_tools.

    Args:
        level: Logging level. If None, will use the default level.
        format_str: Logging format string. If None, will use the default format.
        log_file: Path to the log file. If None and log_to_file is True, will
            use a default location.
        log_to_console: Whether to log to the console.
        log_to_file: Whether to log to a file.
        config: Additional configuration for logging.
    """
    # Get the root logger
    logger = logging.getLogger("projects_tools")

    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Set level
    if level is None:
        level = DEFAULT_LEVEL
    elif isinstance(level, str):
        level = getattr(logging, level.upper())
    logger.setLevel(level)

    # Set format
    if format_str is None:
        format_str = DEFAULT_FORMAT
    formatter = logging.Formatter(format_str)

    # Add console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add file handler
    if log_to_file:
        if log_file is None:
            log_file = Path.home() / ".projects_tools" / "logs" / "projects_tools.log"
        
        # Create directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Apply additional configuration
    if config:
        # Configure specific loggers
        for logger_name, logger_config in config.get("loggers", {}).items():
            logger = logging.getLogger(logger_name)
            if "level" in logger_config:
                level = logger_config["level"]
                if isinstance(level, str):
                    level = getattr(logging, level.upper())
                logger.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a module.

    Args:
        name: Name of the module.

    Returns:
        Logger instance.
    """
    return logging.getLogger(f"projects_tools.{name}")
