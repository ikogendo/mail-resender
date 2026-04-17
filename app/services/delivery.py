from __future__ import annotations

import logging

from app.adapters.messengers.base import MessengerAdapter

logger = logging.getLogger(__name__)


class DeliveryService:
    def __init__(self, adapters: dict[str, MessengerAdapter]) -> None:
        self._adapters = adapters

    def deliver(self, channel: str, text: str) -> None:
        adapter = self._adapters.get(channel)
        if adapter is None:
            raise ValueError(f"Unknown channel: {channel}")
        logger.info("Delivering message via %s", channel)
        adapter.send(text)
