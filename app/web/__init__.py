from __future__ import annotations

from pathlib import Path

from flask import Flask

from app.config import get_settings
from app.logging_config import configure_logging
from app.metrics.endpoint import register_metrics_route
from app.web.blueprints.main import main_blueprint


def create_app() -> Flask:
    settings = get_settings()
    configure_logging()

    project_root = Path(__file__).resolve().parents[2]
    app = Flask(
        settings.app_name,
        template_folder=str(project_root / "templates"),
        static_folder=str(project_root / "static"),
    )
    app.config["SECRET_KEY"] = settings.secret_key
    app.register_blueprint(main_blueprint)

    if settings.metrics_enabled:
        register_metrics_route(app, settings.metrics_path)

    return app
