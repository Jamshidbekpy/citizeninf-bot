"""
Structured logging: JSON in production, console for dev.
Loyiha logikasiga ta'sir qilmaydi — faqat log yozish.
"""
import logging
import sys

import structlog

from app.config import config


def setup_logging() -> None:
    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer() if _is_json_logging() else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def _is_json_logging() -> bool:
    """LOG_FORMAT=json bo'lsa JSON, aks holda console."""
    import os
    return os.getenv("LOG_FORMAT", "").upper() == "JSON"


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)
