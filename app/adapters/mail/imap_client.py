from __future__ import annotations

from dataclasses import dataclass
import logging

from app.config import Settings

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class MailEnvelope:
    message_id: str
    sender: str
    subject: str
    body: str


class IMAPClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def poll_unseen(self) -> list[MailEnvelope]:
        logger.debug(
            "Polling IMAP host=%s port=%s ssl=%s",
            self._settings.imap_host,
            self._settings.imap_port,
            self._settings.imap_use_ssl,
        )
        return []
