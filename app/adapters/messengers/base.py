from __future__ import annotations

from abc import ABC, abstractmethod


class MessengerAdapter(ABC):
    @abstractmethod
    def send(self, text: str) -> None:
        raise NotImplementedError
