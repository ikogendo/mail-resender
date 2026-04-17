from flask import Flask, redirect, url_for

from .extensions import db
from .web import BLUEPRINTS


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__, template_folder="templates")
    app.config.update(
        SECRET_KEY="dev-secret",
        SQLALCHEMY_DATABASE_URI="sqlite:///mail_resender.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=True,
    )
    if config:
        app.config.update(config)

    db.init_app(app)

    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)

    @app.get("/")
    def index():
        return redirect(url_for("status.dashboard"))

    with app.app_context():
        db.create_all()

    return app
