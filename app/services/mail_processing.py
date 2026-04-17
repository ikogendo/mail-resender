from __future__ import annotations

import logging
from dataclasses import dataclass

from app.adapters.mail.imap_client import IMAPClient, MailEnvelope
from app.metrics.collector import METRICS
from app.services.delivery import DeliveryService
from app.services.routing import Router

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ProcessResult:
    processed: int = 0


class MailProcessor:
    def __init__(self, imap_client: IMAPClient, router: Router, delivery: DeliveryService) -> None:
        self._imap_client = imap_client
        self._router = router
        self._delivery = delivery

    def process_batch(self) -> ProcessResult:
        messages = self._imap_client.poll_unseen()
        processed = 0
        for message in messages:
            self._process_single(message)
            processed += 1
        return ProcessResult(processed=processed)

    def _process_single(self, envelope: MailEnvelope) -> None:
        with METRICS.processing_time.time():
            channel = self._router.pick_channel(envelope.subject)
            text = f"From: {envelope.sender}\nSubject: {envelope.subject}\n\n{envelope.body}"
            self._delivery.deliver(channel, text)
            METRICS.delivery_counter.labels(channel=channel, status="success").inc()
            logger.info("Message %s delivered via %s", envelope.message_id, channel)
