from __future__ import annotations

from abc import abstractmethod
from typing import Protocol

from app.models.messages import DeliveryResult, OutboundMessage


class MessengerAdapter(Protocol):
    @abstractmethod
    def send(self, message: OutboundMessage) -> DeliveryResult:
        raise NotImplementedError
