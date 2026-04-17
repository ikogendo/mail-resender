from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Route:
    pattern: str
    channel: str


class Router:
    def __init__(self, routes: list[Route] | None = None) -> None:
        self._routes = routes or [Route(pattern="*", channel="telegram")]

    def pick_channel(self, subject: str) -> str:
        normalized = subject.lower()
        for route in self._routes:
            if route.pattern == "*" or route.pattern.lower() in normalized:
                return route.channel
        return "telegram"
