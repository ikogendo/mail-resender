from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DeliveryChannelType(str, Enum):
    TELEGRAM = "telegram"
    MATTERMOST = "mattermost"


@dataclass(slots=True)
class DeliveryChannel:
    type: DeliveryChannelType | str
    config: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class OutboundMessage:
    text: str
    subject: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DeliveryLog:
    channel_type: str
    success: bool
    status_code: int | None = None
    error: str | None = None
    response_body: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DeliveryResult:
    success: bool
    logs: list[DeliveryLog] = field(default_factory=list)

    @classmethod
    def ok(cls, *logs: DeliveryLog) -> "DeliveryResult":
        return cls(success=True, logs=list(logs))

    @classmethod
    def failed(cls, *logs: DeliveryLog) -> "DeliveryResult":
        return cls(success=False, logs=list(logs))
