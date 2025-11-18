"""Structured logging configuration with JSON support.

This module provides a centralized logging system with support for both
JSON (production) and text (development) formats.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from watsonx_agent_creator.core.config import get_settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging.

    This formatter outputs log records as JSON objects for easy parsing
    and integration with log aggregation systems.

    Attributes:
        app_name: Application name to include in log records
    """

    def __init__(self, app_name: str = "watsonx-agent-creator") -> None:
        """Initialize the JSON formatter.

        Args:
            app_name: Application name to include in logs
        """
        super().__init__()
        self.app_name = app_name

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON-formatted log string
        """
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "app": self.app_name,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Add file and line number in debug mode
        if record.levelno == logging.DEBUG:
            log_data.update(
                {
                    "file": record.pathname,
                    "line": record.lineno,
                    "function": record.funcName,
                }
            )

        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for terminal output.

    This formatter adds ANSI color codes to log messages for better
    readability in terminal environments.
    """

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors.

        Args:
            record: Log record to format

        Returns:
            Colored log string
        """
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{self.BOLD}{record.levelname}{self.RESET}"
        record.name = f"{self.BOLD}{record.name}{self.RESET}"
        return super().format(record)


def setup_logging(
    log_level: str | None = None,
    log_format: str | None = None,
    log_file: Path | None = None,
) -> None:
    """Configure application-wide logging.

    Sets up logging with either JSON or colored text format, and optionally
    writes logs to a file.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format ('json' or 'text')
        log_file: Optional path to log file

    Examples:
        >>> setup_logging(log_level="DEBUG", log_format="text")
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
    """
    settings = get_settings()
    level = log_level or settings.log_level
    format_type = log_format or settings.log_format

    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set log level
    root_logger.setLevel(getattr(logging, level.upper()))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))

    if format_type == "json":
        formatter = JSONFormatter(app_name=settings.app_name)
    else:
        formatter = ColoredFormatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(JSONFormatter(app_name=settings.app_name))
        root_logger.addHandler(file_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the specified module.

    Args:
        name: Logger name (typically __name__ of the calling module)

    Returns:
        Configured logger instance

    Examples:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing started")
        >>> logger.error("An error occurred", extra={"extra_fields": {"user_id": 123}})
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that adds contextual information to log records.

    This adapter allows adding consistent extra fields to all log messages
    from a specific context.

    Examples:
        >>> logger = get_logger(__name__)
        >>> context_logger = LoggerAdapter(logger, {"agent_name": "my_agent"})
        >>> context_logger.info("Generation started")  # Will include agent_name in JSON logs
    """

    def process(
        self, msg: str, kwargs: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        """Process log message and add extra fields.

        Args:
            msg: Log message
            kwargs: Additional keyword arguments

        Returns:
            Tuple of (message, modified kwargs with extra fields)
        """
        # Add context to extra fields
        if "extra" not in kwargs:
            kwargs["extra"] = {}

        kwargs["extra"]["extra_fields"] = self.extra

        return msg, kwargs
