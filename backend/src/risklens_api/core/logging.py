from __future__ import annotations

import json
import logging
import sys
from typing import Any

# Optional structured fields that services may attach via ``extra=`` and that
# the formatter should surface in CloudWatch. Kept to an explicit allowlist so
# arbitrary record attributes are never serialized by accident.
_OPTIONAL_LOG_FIELDS = (
    "model_id",
    "max_tokens",
    "attempt",
    "stop_reason",
    "input_tokens",
    "output_tokens",
    "truncated_by_max_tokens",
    "response_chars",
    "response_snippet",
)


class JsonFormatter(logging.Formatter):
    """Structured JSON log formatter for the RiskLens application."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
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
        for field in _OPTIONAL_LOG_FIELDS:
            if hasattr(record, field):
                log_data[field] = getattr(record, field)
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
