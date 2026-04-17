from __future__ import annotations

import logging
import time

from app.adapters.mail.imap_client import IMAPClient
from app.adapters.messengers.mattermost import MattermostAdapter
from app.adapters.messengers.telegram import TelegramAdapter
from app.config import get_settings
from app.logging_config import configure_logging
from app.services.delivery import DeliveryService
from app.services.mail_processing import MailProcessor
from app.services.routing import Router

logger = logging.getLogger(__name__)


def build_processor() -> MailProcessor:
    settings = get_settings()
    imap_client = IMAPClient(settings)

    adapters = {}
    if settings.telegram_token and settings.telegram_chat_id:
        adapters["telegram"] = TelegramAdapter(settings.telegram_token, settings.telegram_chat_id)
    if settings.mattermost_webhook_url:
        adapters["mattermost"] = MattermostAdapter(settings.mattermost_webhook_url)

    return MailProcessor(
        imap_client=imap_client,
        router=Router(),
        delivery=DeliveryService(adapters=adapters),
    )


def main() -> None:
    settings = get_settings()
    configure_logging()
    processor = build_processor()

    while True:
        result = processor.process_batch()
        logger.info("Worker iteration completed: processed=%s", result.processed)
        time.sleep(settings.worker_poll_interval_seconds)


if __name__ == "__main__":
    main()
