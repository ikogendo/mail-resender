from datetime import datetime

from flask import Blueprint, flash, render_template

from ...extensions import db
from ...forms import TestNotificationForm
from ...models import DeliveryLog, EventLog

bp = Blueprint("test_send", __name__, url_prefix="/test-send")


@bp.route("/", methods=["GET", "POST"])
def send_test_notification():
    form = TestNotificationForm()
    if form.validate_on_submit():
        # UI only enqueues/writes intent; no background polling or dispatch logic here.
        event = EventLog(level="INFO", message=f"Test notification queued for {form.recipient.data}")
        delivery = DeliveryLog(
            channel=f"channel:{form.channel_id.data or 'n/a'}",
            recipient=form.recipient.data,
            status="queued",
            error=None,
            created_at=datetime.utcnow(),
        )
        db.session.add_all([event, delivery])
        db.session.commit()
        flash("Test notification queued", "success")
    return render_template("test_send/form.html", form=form)
