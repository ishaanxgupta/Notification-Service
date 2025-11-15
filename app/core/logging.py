"""Logging configuration for the notification service."""

from __future__ import annotations

import logging
from typing import Optional


def configure_logging(level: str = "INFO") -> None:
    """Configure global logging format."""
    root_logger = logging.getLogger()
    if root_logger.handlers:
        # Avoid configuring logging multiple times.
        for handler in root_logger.handlers:
            handler.setLevel(level.upper())
        root_logger.setLevel(level.upper())
        return

    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    )


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a configured logger."""
    return logging.getLogger(name or "notification_service")




