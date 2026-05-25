import logging
import sys

from config import settings


_LOGGER_CONFIGURED = False

_SILENT_LOGGERS = [
    "graphql",
    "strawberry",
    "httpx",
    "httpcore",
    "tenacity",
]


def configure_root_logger() -> None:
    global _LOGGER_CONFIGURED
    if _LOGGER_CONFIGURED:
        return

    level = settings.LOG_LEVEL.upper()
    root = logging.getLogger()
    root.setLevel(level)

    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root.addHandler(handler)

    for name in _SILENT_LOGGERS:
        logging.getLogger(name).setLevel(logging.CRITICAL + 1)
        logging.getLogger(name).propagate = False

    _LOGGER_CONFIGURED = True


def get_logger(name: str = "app") -> logging.Logger:
    configure_root_logger()
    return logging.getLogger(name)
