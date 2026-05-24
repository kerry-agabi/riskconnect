from __future__ import annotations

import json
import logging
import sys


class JsonFormatter(logging.Formatter):
    """Structured JSON log formatter for the RiskLens application."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, str | None] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "component": getattr(record, "component", "api"),
            "message": record.getMessage(),
        }
        if hasattr(record, "submission_id"):
            log_data["submission_id"] = record.submission_id  # type: ignore[attr-defined]
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id  # type: ignore[attr-defined]
        if hasattr(record, "status"):
            log_data["status"] = record.status  # type: ignore[attr-defined]
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure structured JSON logging for the application."""
    logger = logging.getLogger("risklens")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger


def get_logger() -> logging.Logger:
    """Return the application logger."""
    return logging.getLogger("risklens")
