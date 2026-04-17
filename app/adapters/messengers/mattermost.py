from __future__ import annotations

import logging

import requests

from app.adapters.messengers.base import MessengerAdapter

logger = logging.getLogger(__name__)


class MattermostAdapter(MessengerAdapter):
    def __init__(self, webhook_url: str) -> None:
        self._webhook_url = webhook_url

    def send(self, text: str) -> None:
        response = requests.post(self._webhook_url, json={"text": text}, timeout=10)
        response.raise_for_status()
        logger.debug("Mattermost message sent")
