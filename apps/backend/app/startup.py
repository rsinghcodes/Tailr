"""
Application startup.
"""

from telemetry.config import configure_logging


def startup() -> None:
    configure_logging()