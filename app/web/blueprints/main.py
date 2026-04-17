from __future__ import annotations

from flask import Blueprint

from app.web.views import index_view, send_test_view

main_blueprint = Blueprint("main", __name__)
main_blueprint.add_url_rule("/", view_func=index_view, methods=["GET"], endpoint="index")
main_blueprint.add_url_rule("/send-test", view_func=send_test_view, methods=["POST"], endpoint="send_test")
