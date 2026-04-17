from __future__ import annotations

from dataclasses import dataclass

from .models import PollingStatus


@dataclass
class StatusSnapshot:
    last_polled_at: object
    last_error: str | None
    processed_count: int
    sent_count: int
    failed_count: int


class StatusService:
    """Read-only status provider for UI.

    Polling and counter updates belong to background workers.
    """

    @staticmethod
    def get_snapshot() -> StatusSnapshot:
        status = PollingStatus.query.order_by(PollingStatus.id.desc()).first()
        if status is None:
            return StatusSnapshot(None, None, 0, 0, 0)
        return StatusSnapshot(
            last_polled_at=status.last_polled_at,
            last_error=status.last_error,
            processed_count=status.processed_count,
            sent_count=status.sent_count,
            failed_count=status.failed_count,
        )
