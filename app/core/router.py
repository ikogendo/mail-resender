"""Simple routing helpers for outgoing channels."""

from __future__ import annotations


def route_channels(subject: str) -> list[str]:
    subject_l = subject.lower()
    if "critical" in subject_l or "urgent" in subject_l:
        return ["telegram", "mattermost"]
    if "telegram" in subject_l:
        return ["telegram"]
    return ["mattermost"]
