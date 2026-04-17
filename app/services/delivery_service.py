from __future__ import annotations

from dataclasses import dataclass

from app.adapters.messengers.base import MessengerAdapter
from app.adapters.messengers.mattermost import MattermostAdapter
from app.adapters.messengers.telegram import TelegramAdapter
from app.models.messages import DeliveryChannel, DeliveryChannelType, DeliveryLog, DeliveryResult, OutboundMessage


@dataclass(slots=True)
class DeliveryService:
    def deliver(self, message: OutboundMessage, channels: list[DeliveryChannel]) -> DeliveryResult:
        all_logs: list[DeliveryLog] = []
        all_ok = True

        for channel in channels:
            try:
                adapter = self._build_adapter(channel)
                result = adapter.send(message)
                all_logs.extend(result.logs)
                if not result.success:
                    all_ok = False
            except Exception as exc:  # noqa: BLE001
                all_ok = False
                all_logs.append(
                    DeliveryLog(
                        channel_type=str(channel.type),
                        success=False,
                        error=f"Unhandled delivery error: {exc}",
                    )
                )

        return DeliveryResult(success=all_ok, logs=all_logs)

    def _build_adapter(self, channel: DeliveryChannel) -> MessengerAdapter:
        channel_type = DeliveryChannelType(channel.type)
        config = channel.config

        if channel_type == DeliveryChannelType.TELEGRAM:
            return TelegramAdapter(
                bot_token=config.get("bot_token", ""),
                chat_id=config.get("chat_id", ""),
                timeout_seconds=float(config.get("timeout_seconds", 10.0)),
                max_message_length=int(config.get("max_message_length", 4096)),
                max_retries=int(config.get("max_retries", 3)),
                backoff_seconds=float(config.get("backoff_seconds", 0.5)),
            )

        if channel_type == DeliveryChannelType.MATTERMOST:
            return MattermostAdapter(
                webhook_url=config.get("webhook_url", ""),
                channel=config.get("channel"),
                username=config.get("username"),
                timeout_seconds=float(config.get("timeout_seconds", 10.0)),
            )

        raise ValueError(f"Unsupported delivery channel type: {channel.type}")
