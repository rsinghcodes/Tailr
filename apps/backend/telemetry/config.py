import logging
import sys

from config.settings import settings

from telemetry.filters import RequestContextFilter
from telemetry.formatters import TailrFormatter


def configure_logging():

    handler = logging.StreamHandler(sys.stdout)

    handler.setFormatter(TailrFormatter())

    handler.addFilter(RequestContextFilter())

    root = logging.getLogger()

    root.handlers.clear()

    root.addHandler(handler)

    root.setLevel(settings.LOG_LEVEL)