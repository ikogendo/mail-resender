"""Internal app metrics and optional Prometheus integration."""

from __future__ import annotations

from collections import defaultdict
from contextlib import contextmanager
from time import perf_counter
from typing import Iterator

from flask import Blueprint, Response


class MetricsCollector:
    """Collects timings and success/error counters."""

    OPERATIONS = (
        "fetch_mail",
        "parse_mail",
        "db_save",
        "send_telegram",
        "send_mattermost",
    )

    def __init__(self) -> None:
        self.timings = defaultdict(list)
        self.success = defaultdict(int)
        self.errors = defaultdict(int)

    @contextmanager
    def timer(self, operation: str) -> Iterator[None]:
        start = perf_counter()
        try:
            yield
        except Exception:
            self.errors[operation] += 1
            raise
        else:
            self.success[operation] += 1
        finally:
            self.timings[operation].append(perf_counter() - start)

    def snapshot(self) -> dict[str, dict[str, float | int]]:
        result: dict[str, dict[str, float | int]] = {}
        for op in self.OPERATIONS:
            items = self.timings[op]
            avg = sum(items) / len(items) if items else 0.0
            result[op] = {
                "count": len(items),
                "avg_seconds": avg,
                "success": self.success[op],
                "errors": self.errors[op],
            }
        return result


def prometheus_blueprint(enabled: bool) -> Blueprint | None:
    """Expose /metrics when enabled and prometheus_client is available."""
    if not enabled:
        return None

    try:
        from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
    except ImportError:
        return None

    bp = Blueprint("metrics", __name__)

    @bp.get("/metrics")
    def metrics() -> Response:
        return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)

    return bp
