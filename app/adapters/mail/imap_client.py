from __future__ import annotations

import imaplib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FetchedMessage:
    uid: str
    rfc822: bytes


class MailFetcher(ABC):
    """Абстракция для получения писем.

    Метод poll() оставлен как единая точка входа, чтобы в будущем
    можно было подключить IMAP IDLE без изменения worker-слоя.
    """

    @abstractmethod
    def poll(self, folder: str = "INBOX", criteria: str = "UNSEEN") -> list[FetchedMessage]:
        raise NotImplementedError


class ImapClient(MailFetcher):
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        *,
        use_ssl: bool = True,
        timeout: float | None = 30,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.timeout = timeout
        self._client: imaplib.IMAP4 | None = None

    def connect(self) -> None:
        logger.info("Connecting to IMAP server", extra={"host": self.host, "port": self.port})
        if self.use_ssl:
            self._client = imaplib.IMAP4_SSL(self.host, self.port, timeout=self.timeout)
        else:
            self._client = imaplib.IMAP4(self.host, self.port, timeout=self.timeout)

    def login(self) -> None:
        if self._client is None:
            self.connect()
        assert self._client is not None
        status, _ = self._client.login(self.username, self.password)
        self._ensure_ok(status, "login")

    def select_folder(self, folder: str = "INBOX", readonly: bool = True) -> int:
        client = self._require_client()
        status, data = client.select(folder, readonly=readonly)
        self._ensure_ok(status, f"select {folder}")
        message_count = int(data[0]) if data and data[0] else 0
        return message_count

    def search(self, criteria: str = "UNSEEN") -> list[bytes]:
        client = self._require_client()
        status, data = client.search(None, criteria)
        self._ensure_ok(status, f"search {criteria}")
        if not data or not data[0]:
            return []
        return [token for token in data[0].split() if token]

    def fetch(self, message_ids: Iterable[bytes]) -> list[FetchedMessage]:
        client = self._require_client()
        fetched: list[FetchedMessage] = []

        for message_id in message_ids:
            status, data = client.fetch(message_id, "(RFC822 UID)")
            self._ensure_ok(status, f"fetch {message_id!r}")
            uid = self._extract_uid(data)
            body = self._extract_rfc822(data)
            if uid and body:
                fetched.append(FetchedMessage(uid=uid, rfc822=body))

        return fetched

    def poll(self, folder: str = "INBOX", criteria: str = "UNSEEN") -> list[FetchedMessage]:
        """Получить новые сообщения через select + search + fetch."""
        if self._client is None:
            self.connect()
            self.login()

        self.select_folder(folder)
        message_ids = self.search(criteria)
        if not message_ids:
            return []

        return self.fetch(message_ids)

    def close(self) -> None:
        if self._client is None:
            return
        try:
            self._client.close()
        except Exception:  # noqa: BLE001
            # close может падать, если папка не была успешно select
            pass
        try:
            self._client.logout()
        except Exception:  # noqa: BLE001
            pass
        self._client = None

    def _require_client(self) -> imaplib.IMAP4:
        if self._client is None:
            raise RuntimeError("IMAP client is not connected")
        return self._client

    @staticmethod
    def _ensure_ok(status: str, action: str) -> None:
        if status != "OK":
            raise RuntimeError(f"IMAP action failed: {action}, status={status}")

    @staticmethod
    def _extract_uid(fetch_data: list[object] | tuple[object, ...] | None) -> str | None:
        if not fetch_data:
            return None

        for chunk in fetch_data:
            if not isinstance(chunk, tuple):
                continue
            metadata = chunk[0]
            if not isinstance(metadata, bytes):
                continue
            text = metadata.decode(errors="replace")
            marker = "UID "
            if marker in text:
                uid = text.split(marker, 1)[1].split(" ", 1)[0].strip(") ")
                return uid

        return None

    @staticmethod
    def _extract_rfc822(fetch_data: list[object] | tuple[object, ...] | None) -> bytes | None:
        if not fetch_data:
            return None
        for chunk in fetch_data:
            if isinstance(chunk, tuple) and len(chunk) > 1 and isinstance(chunk[1], bytes):
                return chunk[1]
        return None
