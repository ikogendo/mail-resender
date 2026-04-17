from flask import Blueprint, render_template

from ...models import DeliveryLog, EventLog

bp = Blueprint("events", __name__, url_prefix="/events")


@bp.get("/")
def recent_events():
    event_logs = EventLog.query.order_by(EventLog.created_at.desc()).limit(50).all()
    delivery_logs = DeliveryLog.query.order_by(DeliveryLog.created_at.desc()).limit(50).all()
    return render_template("events/recent.html", event_logs=event_logs, delivery_logs=delivery_logs)
