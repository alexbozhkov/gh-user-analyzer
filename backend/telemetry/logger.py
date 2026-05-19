import logging
import os


_LOGGER_CONFIGURED = False


def configure_root_logger() -> None:
    global _LOGGER_CONFIGURED
    if _LOGGER_CONFIGURED:
        return

    level = os.getenv("LOG_LEVEL", "INFO").upper()
    root = logging.getLogger()
    root.setLevel(level)

    root.handlers.clear()

    handler = logging.StreamHandler()
    root.addHandler(handler)

    _LOGGER_CONFIGURED = True


def get_logger(name: str = "app") -> logging.Logger:
    configure_root_logger()
    return logging.getLogger(name)
