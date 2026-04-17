"""In-memory deduplication for message ids."""

from __future__ import annotations


class Deduplicator:
    def __init__(self) -> None:
        self._seen: set[str] = set()

    def is_duplicate(self, message_id: str) -> bool:
        if message_id in self._seen:
            return True
        self._seen.add(message_id)
        return False
