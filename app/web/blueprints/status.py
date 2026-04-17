from flask import Blueprint, render_template

from ...services import StatusService

bp = Blueprint("status", __name__, url_prefix="/status")


@bp.get("/")
def dashboard():
    snapshot = StatusService.get_snapshot()
    return render_template("status/dashboard.html", snapshot=snapshot)
