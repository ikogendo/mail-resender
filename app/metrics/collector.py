from __future__ import annotations

from dataclasses import dataclass

from prometheus_client import Counter, Summary


@dataclass(frozen=True)
class Metrics:
    processing_time: Summary
    delivery_counter: Counter


METRICS = Metrics(
    processing_time=Summary(
        "mailbridge_processing_seconds",
        "Time spent processing a single message",
    ),
    delivery_counter=Counter(
        "mailbridge_delivery_total",
        "Number of delivery attempts",
        labelnames=("channel", "status"),
    ),
)
