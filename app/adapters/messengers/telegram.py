from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.adapters.messengers.base import MessengerAdapter
from app.models.messages import DeliveryLog, DeliveryResult, OutboundMessage


@dataclass(slots=True)
class TelegramAdapter(MessengerAdapter):
    bot_token: str
    chat_id: str
    timeout_seconds: float = 10.0
    max_message_length: int = 4096
    max_retries: int = 3
    backoff_seconds: float = 0.5

    def send(self, message: OutboundMessage) -> DeliveryResult:
        if not self.bot_token:
            return DeliveryResult.failed(
                DeliveryLog(channel_type="telegram", success=False, error="Missing bot token")
            )
        if not self.chat_id:
            return DeliveryResult.failed(
                DeliveryLog(channel_type="telegram", success=False, error="Missing chat_id")
            )

        chunks = self._chunk_message(message.text)
        logs: list[DeliveryLog] = []

        for idx, chunk in enumerate(chunks, start=1):
            chunk_result = self._send_chunk(chunk=chunk, part=idx, total_parts=len(chunks))
            logs.extend(chunk_result.logs)
            if not chunk_result.success:
                return DeliveryResult.failed(*logs)

        return DeliveryResult.ok(*logs)

    def _chunk_message(self, text: str) -> list[str]:
        if len(text) <= self.max_message_length:
            return [text]
        return [
            text[i : i + self.max_message_length]
            for i in range(0, len(text), self.max_message_length)
        ]

    def _send_chunk(self, chunk: str, part: int, total_parts: int) -> DeliveryResult:
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": chunk,
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                body = json.dumps(payload).encode("utf-8")
                req = Request(
                    url=url,
                    data=body,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urlopen(req, timeout=self.timeout_seconds) as response:
                    status = response.getcode()
                    raw = response.read().decode("utf-8", errors="replace")
                    if 200 <= status < 300:
                        return DeliveryResult.ok(
                            DeliveryLog(
                                channel_type="telegram",
                                success=True,
                                status_code=status,
                                response_body=raw,
                                metadata={"part": part, "total_parts": total_parts},
                            )
                        )
                    return DeliveryResult.failed(
                        DeliveryLog(
                            channel_type="telegram",
                            success=False,
                            status_code=status,
                            error=self._parse_telegram_error(raw),
                            response_body=raw,
                            metadata={"part": part, "total_parts": total_parts},
                        )
                    )
            except HTTPError as exc:
                raw = exc.read().decode("utf-8", errors="replace")
                return DeliveryResult.failed(
                    DeliveryLog(
                        channel_type="telegram",
                        success=False,
                        status_code=exc.code,
                        error=self._parse_telegram_error(raw),
                        response_body=raw,
                        metadata={"part": part, "total_parts": total_parts},
                    )
                )
            except URLError as exc:
                if attempt >= self.max_retries:
                    return DeliveryResult.failed(
                        DeliveryLog(
                            channel_type="telegram",
                            success=False,
                            error=f"Network error after {attempt} attempts: {exc.reason}",
                            metadata={"part": part, "total_parts": total_parts},
                        )
                    )
                time.sleep(self.backoff_seconds * (2 ** (attempt - 1)))

        return DeliveryResult.failed(
            DeliveryLog(
                channel_type="telegram",
                success=False,
                error="Exceeded retry attempts",
                metadata={"part": part, "total_parts": total_parts},
            )
        )

    @staticmethod
    def _parse_telegram_error(raw: str) -> str:
        try:
            parsed: dict[str, Any] = json.loads(raw)
        except json.JSONDecodeError:
            return raw.strip() or "Unknown Telegram API error"

        description = parsed.get("description")
        if isinstance(description, str) and description.strip():
            return description

        return raw.strip() or "Unknown Telegram API error"
