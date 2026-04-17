from __future__ import annotations

from flask import Flask, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest


def register_metrics_route(app: Flask, path: str = "/metrics") -> None:
    def metrics_view() -> Response:
        payload = generate_latest()
        return Response(payload, mimetype=CONTENT_TYPE_LATEST)

    app.add_url_rule(path, endpoint="metrics", view_func=metrics_view)
