"""
Logging configuration for the application.
"""

import logging.config
import sys
from typing import Any, Dict

from loguru import logger
from pydantic import BaseModel

from app.core.config import settings


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentation.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = "resume_parser"
    LOG_FORMAT: str = "<level>{level: <8}</level> <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> request_id={extra[request_id]} <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: Dict[str, Any] = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers: Dict[str, Any] = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "formatter": "default",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 10000000,  # 10MB
            "backupCount": 5,
        },
    }
    loggers: Dict[str, Any] = {
        "resume_parser": {"handlers": ["default", "file"], "level": LOG_LEVEL},
    }


def setup_logging() -> None:
    """Configure logging for the application."""
    # Remove all existing handlers
    logging.getLogger().handlers = []

    # Intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(settings.LOG_LEVEL)

    # Remove every other logger's handlers and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # Define simple log format without request_id (can be added later via middleware)
    log_format = "<level>{level: <8}</level> <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
    
    # Configure loguru
    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "format": log_format,
                "level": settings.LOG_LEVEL,
            },
            {
                "sink": "logs/app.log",
                "format": log_format,
                "level": settings.LOG_LEVEL,
                "rotation": "10 MB",
                "retention": "1 week",
                "compression": "zip",
            },
        ]
    )