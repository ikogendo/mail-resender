"""Application configuration loading from TOML and environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

CONFIG_PATH = Path("/etc/mailbridge/config.toml")
ENV_PREFIX = "MAILBRIDGE_"


@dataclass(frozen=True)
class RetryPolicy:
    max_retries: int = 3
    backoff_seconds: float = 1.0


@dataclass(frozen=True)
class FlaskConfig:
    host: str = "0.0.0.0"
    port: int = 8080


@dataclass(frozen=True)
class AppConfig:
    app_name: str = "mailbridge"
    sqlite_path: str = "/data/mailbridge.db"
    log_dir: str = "/var/log/mailbridge"
    polling_interval_seconds: int = 30
    flask: FlaskConfig = FlaskConfig()
    secret_key: str = "change-me"
    profiling_enabled: bool = False
    metrics_enabled: bool = True
    timezone: str = "UTC"
    retry_policy: RetryPolicy = RetryPolicy()


def _to_bool(value: str | bool | None, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _read_toml(path: Path = CONFIG_PATH) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("rb") as fh:
        return tomllib.load(fh)


def _env(name: str) -> str | None:
    return os.getenv(f"{ENV_PREFIX}{name}")


def load_config(path: Path = CONFIG_PATH) -> AppConfig:
    raw = _read_toml(path)

    app_name = _env("APP_NAME") or raw.get("app_name", "mailbridge")
    sqlite_path = _env("SQLITE_PATH") or raw.get("sqlite_path", "/data/mailbridge.db")
    log_dir = _env("LOG_DIR") or raw.get("log_dir", "/var/log/mailbridge")

    polling_interval_seconds = int(
        _env("POLLING_INTERVAL_SECONDS")
        or raw.get("polling_interval_seconds", 30)
    )

    flask_raw = raw.get("flask", {})
    flask = FlaskConfig(
        host=_env("FLASK_HOST") or flask_raw.get("host", "0.0.0.0"),
        port=int(_env("FLASK_PORT") or flask_raw.get("port", 8080)),
    )

    secret_key = _env("SECRET_KEY") or raw.get("secret_key", "change-me")
    profiling_enabled = _to_bool(
        _env("PROFILING_ENABLED"), raw.get("profiling_enabled", False)
    )
    metrics_enabled = _to_bool(_env("METRICS_ENABLED"), raw.get("metrics_enabled", True))
    timezone = _env("TIMEZONE") or raw.get("timezone", "UTC")

    retry_raw = raw.get("retry_policy", {})
    retry_policy = RetryPolicy(
        max_retries=int(_env("RETRY_MAX_RETRIES") or retry_raw.get("max_retries", 3)),
        backoff_seconds=float(
            _env("RETRY_BACKOFF_SECONDS") or retry_raw.get("backoff_seconds", 1.0)
        ),
    )

    return AppConfig(
        app_name=app_name,
        sqlite_path=sqlite_path,
        log_dir=log_dir,
        polling_interval_seconds=polling_interval_seconds,
        flask=flask,
        secret_key=secret_key,
        profiling_enabled=profiling_enabled,
        metrics_enabled=metrics_enabled,
        timezone=timezone,
        retry_policy=retry_policy,
    )
