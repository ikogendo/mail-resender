from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from tenacity import RetryError, Retrying, stop_after_attempt, wait_exponential

from app.adapters.mail.imap_client import ImapClient
from app.services.mail_parser import MailParser, ParsedMail


@dataclass(frozen=True)
class MailAccount:
    id: int
    email: str
    imap_host: str
    imap_port: int
    username: str
    password: str
    folder: str = "INBOX"
    search_criteria: str = "UNSEEN"


class AccountRepository(Protocol):
    def get_active_accounts(self) -> list[MailAccount]: ...


class ProcessedEmailRepository(Protocol):
    def exists(self, account_id: int, dedup_key: str) -> bool: ...

    def create(self, account_id: int, dedup_key: str, uid: str, message_id: str | None) -> None: ...


class EventLogRepository(Protocol):
    def info(self, account_id: int, stage: str, message: str) -> None: ...

    def error(self, account_id: int, stage: str, message: str) -> None: ...


class OutboundSender(Protocol):
    def send(self, account: MailAccount, message_uid: str, mail: ParsedMail) -> None: ...


def build_file_logger(log_file: str = "logs/mail_worker.log") -> logging.Logger:
    logger = logging.getLogger("mail_worker")
    if logger.handlers:
        return logger

    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] [account=%(account_id)s] %(message)s")
    )

    logger.addHandler(file_handler)
    logger.propagate = False
    return logger


class MailWorker:
    def __init__(
        self,
        account_repository: AccountRepository,
        processed_email_repository: ProcessedEmailRepository,
        event_log_repository: EventLogRepository,
        outbound_sender: OutboundSender,
        *,
        parser: MailParser | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.account_repository = account_repository
        self.processed_email_repository = processed_email_repository
        self.event_log_repository = event_log_repository
        self.outbound_sender = outbound_sender
        self.parser = parser or MailParser()
        self.logger = logger or build_file_logger()

    def poll_once(self) -> None:
        accounts = self.account_repository.get_active_accounts()
        for account in accounts:
            try:
                self._process_account(account)
            except Exception as exc:  # noqa: BLE001
                self._log_error(account.id, "account_failed", str(exc))

    def _process_account(self, account: MailAccount) -> None:
        self._log_info(account.id, "account_start", f"Start polling for {account.email}")

        client = ImapClient(
            host=account.imap_host,
            port=account.imap_port,
            username=account.username,
            password=account.password,
        )

        try:
            messages = self._retry_imap_poll(client, account)
            self._log_info(account.id, "poll_done", f"Fetched {len(messages)} messages")

            for fetched in messages:
                try:
                    parsed = self.parser.parse(fetched.rfc822)
                    dedup_key = self._dedup_key(account.id, parsed)

                    if self.processed_email_repository.exists(account.id, dedup_key):
                        self._log_info(
                            account.id,
                            "duplicate_skipped",
                            f"UID={fetched.uid}, dedup_key={dedup_key}",
                        )
                        continue

                    self.outbound_sender.send(account, fetched.uid, parsed)
                    self.processed_email_repository.create(
                        account_id=account.id,
                        dedup_key=dedup_key,
                        uid=fetched.uid,
                        message_id=parsed.message_id,
                    )
                    self._log_info(account.id, "message_processed", f"UID={fetched.uid}")
                except Exception as exc:  # noqa: BLE001
                    self._log_error(account.id, "message_failed", f"UID={fetched.uid}: {exc}")
        finally:
            client.close()
            self._log_info(account.id, "account_end", f"End polling for {account.email}")

    def _retry_imap_poll(self, client: ImapClient, account: MailAccount):
        retrying = Retrying(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=15), reraise=True)
        try:
            for attempt in retrying:
                with attempt:
                    self._log_info(account.id, "imap_poll_attempt", f"Attempt {attempt.retry_state.attempt_number}")
                    return client.poll(folder=account.folder, criteria=account.search_criteria)
        except RetryError as exc:
            raise RuntimeError("IMAP polling failed after retries") from exc

    @staticmethod
    def _normalize_message_id(message_id: str | None) -> str | None:
        if not message_id:
            return None
        normalized = message_id.strip().lower()
        return normalized.strip("<>")

    def _dedup_key(self, account_id: int, mail: ParsedMail) -> str:
        normalized_message_id = self._normalize_message_id(mail.message_id)
        if normalized_message_id:
            return f"{account_id}:{normalized_message_id}"

        fallback = "|".join(
            [
                mail.message_id or "",
                mail.date.isoformat() if mail.date else "",
                mail.from_address or "",
                mail.subject or "",
            ]
        )
        digest = hashlib.sha256(fallback.encode("utf-8", errors="replace")).hexdigest()
        return f"{account_id}:fallback:{digest}"

    def _log_info(self, account_id: int, stage: str, message: str) -> None:
        self.event_log_repository.info(account_id, stage, message)
        self.logger.info(f"[{stage}] {message}", extra={"account_id": account_id})

    def _log_error(self, account_id: int, stage: str, message: str) -> None:
        self.event_log_repository.error(account_id, stage, message)
        self.logger.error(f"[{stage}] {message}", extra={"account_id": account_id})
