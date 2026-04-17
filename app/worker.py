"""Worker process skeleton for polling mailbox and dispatching notifications."""

from __future__ import annotations

import logging
import time

from app.config import load_config
from app.db import create_schema, init_engine
from app.logging_config import configure_logging
from app.metrics.collector import MetricsCollector

logger = logging.getLogger(__name__)


def run_worker() -> None:
    cfg = load_config()
    configure_logging(cfg.log_dir, docker_mode=False)

    engine = init_engine(cfg.sqlite_path)
    create_schema(engine)

    metrics = MetricsCollector()
    logger.info("worker started")

    while True:
        with metrics.timer("fetch_mail"):
            time.sleep(0.01)
        with metrics.timer("parse_mail"):
            time.sleep(0.01)
        time.sleep(cfg.polling_interval_seconds)


if __name__ == "__main__":
    run_worker()
