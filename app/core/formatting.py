"""Message formatting for Telegram and Mattermost."""

from __future__ import annotations


def format_message(channel: str, subject: str, body: str) -> str:
    if channel == "telegram":
        return f"📨 *{subject}*\n\n{body}"
    if channel == "mattermost":
        return f"### {subject}\n{body}"
    raise ValueError(f"Unsupported channel: {channel}")
