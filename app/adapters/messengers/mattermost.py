from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from app.adapters.messengers.base import MessengerAdapter
from app.models.messages import DeliveryLog, DeliveryResult, OutboundMessage


@dataclass(slots=True)
class MattermostAdapter(MessengerAdapter):
    webhook_url: str
    channel: str | None = None
    username: str | None = None
    timeout_seconds: float = 10.0

    def send(self, message: OutboundMessage) -> DeliveryResult:
        channel_validation_error = self._validate_channel()
        if channel_validation_error:
            return DeliveryResult.failed(
                DeliveryLog(
                    channel_type="mattermost",
                    success=False,
                    error=channel_validation_error,
                )
            )

        payload: dict[str, str] = {"text": message.text}
        if self.channel:
            payload["channel"] = self.channel
        if self.username:
            payload["username"] = self.username

        body = json.dumps(payload).encode("utf-8")
        req = Request(
            url=self.webhook_url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(req, timeout=self.timeout_seconds) as response:
                status = response.getcode()
                raw = response.read().decode("utf-8", errors="replace")
                if 200 <= status < 300:
                    return DeliveryResult.ok(
                        DeliveryLog(
                            channel_type="mattermost",
                            success=True,
                            status_code=status,
                            response_body=raw,
                        )
                    )
                return DeliveryResult.failed(
                    DeliveryLog(
                        channel_type="mattermost",
                        success=False,
                        status_code=status,
                        error=f"Mattermost webhook returned HTTP {status}",
                        response_body=raw,
                    )
                )
        except HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            return DeliveryResult.failed(
                DeliveryLog(
                    channel_type="mattermost",
                    success=False,
                    status_code=exc.code,
                    error=f"Mattermost webhook returned HTTP {exc.code}",
                    response_body=raw,
                )
            )
        except URLError as exc:
            return DeliveryResult.failed(
                DeliveryLog(
                    channel_type="mattermost",
                    success=False,
                    error=f"Mattermost network error: {exc.reason}",
                )
            )

    def _validate_channel(self) -> str | None:
        if not self.webhook_url:
            return "Missing Mattermost webhook_url"

        parsed = urlparse(self.webhook_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return "Invalid Mattermost webhook_url"

        if self.channel is None:
            return None

        if not self.channel.strip():
            return "Mattermost channel cannot be empty"

        first = self.channel[0]
        if first not in {"#", "@"}:
            return "Mattermost channel must start with # (channel) or @ (user)"

        return None
