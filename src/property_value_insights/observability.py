"""Structured logging and isolated Prometheus metrics for the API."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime

from prometheus_client import CollectorRegistry, Counter, Histogram, generate_latest
from prometheus_client.exposition import CONTENT_TYPE_LATEST


class JsonFormatter(logging.Formatter):
    """Render operational log records as one JSON object per line."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in (
            "request_id",
            "method",
            "path",
            "status_code",
            "duration_ms",
            "model_version",
            "prediction_count",
        ):
            if hasattr(record, field):
                payload[field] = getattr(record, field)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def configure_logging(level: str) -> logging.Logger:
    """Configure the service logger without mutating the root logger."""

    logger = logging.getLogger("property_value_insights.api")
    logger.setLevel(level.upper())
    logger.propagate = False
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    return logger


class OperationalMetrics:
    """Prometheus collectors owned by one application instance."""

    def __init__(self) -> None:
        self.registry = CollectorRegistry()
        self.requests = Counter(
            "pvi_http_requests_total",
            "HTTP requests processed by the service.",
            ("method", "route", "status"),
            registry=self.registry,
        )
        self.duration = Histogram(
            "pvi_http_request_duration_seconds",
            "HTTP request duration in seconds.",
            ("method", "route"),
            registry=self.registry,
        )
        self.predictions = Counter(
            "pvi_predictions_total",
            "Property predictions returned by mode.",
            ("mode",),
            registry=self.registry,
        )
        self.failures = Counter(
            "pvi_request_failures_total",
            "Unhandled request failures.",
            ("exception_type",),
            registry=self.registry,
        )

    def render(self) -> tuple[bytes, str]:
        return generate_latest(self.registry), CONTENT_TYPE_LATEST
