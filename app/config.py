from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = Field(default="mailbridge")
    environment: Literal["development", "staging", "production"] = "development"

    database_url: str = Field(default="sqlite+pysqlite:///./mailbridge.db")
    imap_host: str = Field(default="localhost")
    imap_port: int = Field(default=993)
    imap_username: str = Field(default="")
    imap_password: str = Field(default="")
    imap_use_ssl: bool = Field(default=True)

    telegram_token: str | None = Field(default=None)
    telegram_chat_id: str | None = Field(default=None)
    mattermost_webhook_url: str | None = Field(default=None)

    worker_poll_interval_seconds: int = Field(default=30)

    metrics_enabled: bool = Field(default=True)
    metrics_path: str = Field(default="/metrics")

    secret_key: str = Field(default="change-me")

    model_config = SettingsConfigDict(
        env_prefix="MAILBRIDGE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def config_example_path(self) -> Path:
        return Path("etc/mailbridge/config.example.toml")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
