"""Logging configuration utilities."""

from __future__ import annotations

import json
import logging
from logging.config import dictConfig
from pathlib import Path


class JsonFormatter(logging.Formatter):
    """A compact JSON formatter for container stdout logs."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "time": self.formatTime(record, self.datefmt),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(log_dir: str, docker_mode: bool = False) -> None:
    """Configure either file-based or container stdout logging."""
    if docker_mode:
        dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "json": {
                        "()": JsonFormatter,
                        "datefmt": "%Y-%m-%dT%H:%M:%S%z",
                    }
                },
                "handlers": {
                    "stdout": {
                        "class": "logging.StreamHandler",
                        "formatter": "json",
                    }
                },
                "root": {"level": "INFO", "handlers": ["stdout"]},
            }
        )
        return

    path = Path(log_dir)
    path.mkdir(parents=True, exist_ok=True)

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "plain": {
                    "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "app_file": {
                    "class": "logging.FileHandler",
                    "filename": str(path / "app.log"),
                    "formatter": "plain",
                    "level": "INFO",
                },
                "error_file": {
                    "class": "logging.FileHandler",
                    "filename": str(path / "error.log"),
                    "formatter": "plain",
                    "level": "ERROR",
                },
            },
            "root": {"level": "INFO", "handlers": ["app_file", "error_file"]},
        }
    )
