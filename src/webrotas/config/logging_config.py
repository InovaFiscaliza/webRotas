"""
Centralized logging configuration for webRotas application.

This module sets up proper logging with rotating file handlers, console output,
and structured formatting. Logs are saved to the ../logs directory.
"""

import logging
import logging.handlers
import sys

from .constants import LOGS_PATH


class ColoredFormatter(logging.Formatter):
    """Formatter that adds color to console output."""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS and sys.stdout.isatty():
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    name: str = "webrotas",
    level: int = logging.DEBUG,
    console_level: int = logging.INFO,
) -> logging.Logger:
    """
    Configure logging for a module.

    Args:
        name: Logger name (typically __name__)
        level: File logging level
        console_level: Console logging level

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Ensure logs directory exists
    LOGS_PATH.mkdir(parents=True, exist_ok=True)

    # Only configure handlers if logger doesn't have them yet
    if logger.handlers:
        return logger

    # File handler with rotation (10 MB per file, keep 10 backups)
    log_file = LOGS_PATH / f"{name.split('.')[-1]}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=10,
    )
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_formatter = ColoredFormatter(
        fmt="[%(levelname)s] %(name)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return setup_logging(name)
