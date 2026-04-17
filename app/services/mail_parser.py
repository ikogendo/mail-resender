from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from email import message_from_bytes
from email.header import decode_header, make_header
from email.message import Message
from email.policy import default
from email.utils import parsedate_to_datetime


@dataclass(frozen=True)
class AttachmentMeta:
    filename: str | None
    content_type: str
    size: int


@dataclass(frozen=True)
class ParsedMail:
    message_id: str | None
    subject: str | None
    from_address: str | None
    to_address: str | None
    date: datetime | None
    text_plain: str | None
    text_html: str | None
    attachments: list[AttachmentMeta]


class MailParser:
    def parse(self, raw_message: bytes) -> ParsedMail:
        msg = message_from_bytes(raw_message, policy=default)

        text_plain, text_html, attachments = self._extract_content(msg)

        return ParsedMail(
            message_id=self._decoded_header(msg, "Message-ID"),
            subject=self._decoded_header(msg, "Subject"),
            from_address=self._decoded_header(msg, "From"),
            to_address=self._decoded_header(msg, "To"),
            date=self._parse_date(self._decoded_header(msg, "Date")),
            text_plain=text_plain,
            text_html=text_html,
            attachments=attachments,
        )

    @staticmethod
    def _decoded_header(msg: Message, name: str) -> str | None:
        value = msg.get(name)
        if not value:
            return None
        try:
            return str(make_header(decode_header(value))).strip() or None
        except Exception:  # noqa: BLE001
            return value.strip() or None

    @staticmethod
    def _parse_date(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return parsedate_to_datetime(value)
        except Exception:  # noqa: BLE001
            return None

    def _extract_content(self, msg: Message) -> tuple[str | None, str | None, list[AttachmentMeta]]:
        text_plain: str | None = None
        text_html: str | None = None
        attachments: list[AttachmentMeta] = []

        for part in msg.walk():
            if part.is_multipart():
                continue

            content_type = part.get_content_type()
            disposition = (part.get_content_disposition() or "").lower()
            payload = part.get_payload(decode=True) or b""

            if disposition == "attachment":
                attachments.append(
                    AttachmentMeta(
                        filename=part.get_filename(),
                        content_type=content_type,
                        size=len(payload),
                    )
                )
                continue

            if content_type == "text/plain" and text_plain is None:
                text_plain = self._decode_part(part, payload)
            elif content_type == "text/html" and text_html is None:
                text_html = self._decode_part(part, payload)

        return text_plain, text_html, attachments

    @staticmethod
    def _decode_part(part: Message, payload: bytes) -> str | None:
        charset = part.get_content_charset() or "utf-8"
        try:
            text = payload.decode(charset, errors="replace")
        except LookupError:
            text = payload.decode("utf-8", errors="replace")
        return text.strip() or None
