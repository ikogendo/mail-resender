from __future__ import annotations

from flask import flash, redirect, render_template, url_for

from app.adapters.messengers.mattermost import MattermostAdapter
from app.adapters.messengers.telegram import TelegramAdapter
from app.config import get_settings
from app.services.delivery import DeliveryService
from app.web.forms import TestMessageForm


def index_view() -> str:
    form = TestMessageForm()
    return render_template("index.html", form=form)


def send_test_view() -> str:
    form = TestMessageForm()
    if form.validate_on_submit():
        settings = get_settings()
        adapters = {}
        if settings.telegram_token and settings.telegram_chat_id:
            adapters["telegram"] = TelegramAdapter(settings.telegram_token, settings.telegram_chat_id)
        if settings.mattermost_webhook_url:
            adapters["mattermost"] = MattermostAdapter(settings.mattermost_webhook_url)

        service = DeliveryService(adapters=adapters)
        service.deliver(form.channel.data, form.message.data)
        flash("Message sent", "success")
    else:
        flash("Validation failed", "error")
    return redirect(url_for("main.index"))
