from flask import Blueprint, flash, redirect, render_template, url_for

from ...extensions import db
from ...forms import DeliveryChannelForm
from ...models import DeliveryChannel

bp = Blueprint("channels", __name__, url_prefix="/channels")


@bp.get("/")
def list_channels():
    channels = DeliveryChannel.query.order_by(DeliveryChannel.id.desc()).all()
    return render_template("channels/list.html", channels=channels)


@bp.route("/new", methods=["GET", "POST"])
def create_channel():
    form = DeliveryChannelForm()
    if form.validate_on_submit():
        channel = DeliveryChannel()
        form.populate_obj(channel)
        db.session.add(channel)
        db.session.commit()
        flash("Delivery channel created", "success")
        return redirect(url_for("channels.list_channels"))
    return render_template("channels/form.html", form=form, page_title="Create delivery channel")


@bp.route("/<int:channel_id>/edit", methods=["GET", "POST"])
def edit_channel(channel_id: int):
    channel = DeliveryChannel.query.get_or_404(channel_id)
    form = DeliveryChannelForm(obj=channel)
    if form.validate_on_submit():
        form.populate_obj(channel)
        db.session.commit()
        flash("Delivery channel updated", "success")
        return redirect(url_for("channels.list_channels"))
    return render_template("channels/form.html", form=form, page_title=f"Edit channel #{channel.id}")
