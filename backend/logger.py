"""Centralized logging configuration for the arbitrage backend service."""
import logging
import sys
from typing import Optional


def setup_logger(
    name: str,
    level: str = "INFO",
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with consistent formatting.

    Args:
        name: Logger name (typically __name__ of the module)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string (optional)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper()))

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))

    # Create formatter
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(funcName)s:%(lineno)d - %(message)s"
        )

    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Get or create a logger with the given name.

    Args:
        name: Logger name (typically __name__ of the module)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Logger instance
    """
    return setup_logger(name, level)
