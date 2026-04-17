"""Flask web application entrypoint."""

from __future__ import annotations

from flask import Flask, jsonify

from app.config import load_config
from app.logging_config import configure_logging
from app.metrics.collector import MetricsCollector, prometheus_blueprint


def create_app() -> Flask:
    cfg = load_config()
    docker_mode = False
    configure_logging(cfg.log_dir, docker_mode=docker_mode)

    app = Flask(cfg.app_name)
    app.config["SECRET_KEY"] = cfg.secret_key
    app.config["PROFILE"] = cfg.profiling_enabled

    collector = MetricsCollector()
    app.extensions["metrics_collector"] = collector

    @app.get("/health")
    def health() -> tuple[dict[str, str], int]:
        return {"status": "ok"}, 200

    @app.get("/stats")
    def stats() -> tuple[dict, int]:
        return jsonify(collector.snapshot()), 200

    bp = prometheus_blueprint(enabled=cfg.metrics_enabled)
    if bp is not None:
        app.register_blueprint(bp)

    return app


app = create_app()
