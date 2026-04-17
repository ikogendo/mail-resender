from __future__ import annotations

import logging

import httpx

from app.adapters.messengers.base import MessengerAdapter

logger = logging.getLogger(__name__)


class TelegramAdapter(MessengerAdapter):
    def __init__(self, token: str, chat_id: str) -> None:
        self._token = token
        self._chat_id = chat_id

    def send(self, text: str) -> None:
        url = f"https://api.telegram.org/bot{self._token}/sendMessage"
        response = httpx.post(url, json={"chat_id": self._chat_id, "text": text}, timeout=10)
        response.raise_for_status()
        logger.debug("Telegram message sent")
