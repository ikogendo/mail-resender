from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampedMixin


class Profile(TimestampedMixin, Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    mail_accounts: Mapped[list[MailAccount]] = relationship(
        secondary="profile_mail_account_links", back_populates="profiles", lazy="selectin"
    )
    channels: Mapped[list[DeliveryChannel]] = relationship(
        secondary="profile_channel_links", back_populates="profiles", lazy="selectin"
    )
    routing_rules: Mapped[list[RoutingRule]] = relationship(
        back_populates="profile", cascade="all, delete-orphan", lazy="selectin"
    )


class MailAccount(TimestampedMixin, Base):
    __tablename__ = "mail_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    password_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    use_ssl: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    folder: Mapped[str] = mapped_column(String(255), default="INBOX", nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    polling_interval_override: Mapped[int | None] = mapped_column(Integer)

    profiles: Mapped[list[Profile]] = relationship(
        secondary="profile_mail_account_links", back_populates="mail_accounts", lazy="selectin"
    )


class DeliveryChannel(TimestampedMixin, Base):
    __tablename__ = "delivery_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    config_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    profiles: Mapped[list[Profile]] = relationship(
        secondary="profile_channel_links", back_populates="channels", lazy="selectin"
    )


class ProfileMailAccountLink(Base):
    __tablename__ = "profile_mail_account_links"

    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), primary_key=True
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("mail_accounts.id", ondelete="CASCADE"), primary_key=True
    )


class ProfileChannelLink(Base):
    __tablename__ = "profile_channel_links"

    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), primary_key=True
    )
    channel_id: Mapped[int] = mapped_column(
        ForeignKey("delivery_channels.id", ondelete="CASCADE"), primary_key=True
    )


class RoutingRule(Base):
    __tablename__ = "routing_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    account_match: Mapped[str | None] = mapped_column(String(255))
    sender_regex: Mapped[str | None] = mapped_column(String(1024))
    subject_regex: Mapped[str | None] = mapped_column(String(1024))
    has_attachments: Mapped[bool | None] = mapped_column(Boolean)
    raw_expr_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    profile: Mapped[Profile] = relationship(back_populates="routing_rules")


class ProcessedEmail(Base):
    __tablename__ = "processed_emails"
    __table_args__ = (UniqueConstraint("dedup_key", name="uq_processed_emails_dedup_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    message_id: Mapped[str] = mapped_column(String(512), nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey("mail_accounts.id"), nullable=False)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(64), nullable=False)
    dedup_key: Mapped[str] = mapped_column(String(512), nullable=False)


class DeliveryLog(Base):
    __tablename__ = "delivery_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    processed_email_id: Mapped[int] = mapped_column(
        ForeignKey("processed_emails.id", ondelete="CASCADE"), nullable=False
    )
    channel_id: Mapped[int] = mapped_column(ForeignKey("delivery_channels.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    error_text: Mapped[str | None] = mapped_column(Text)
    attempt: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class EventLog(Base):
    __tablename__ = "event_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    level: Mapped[str] = mapped_column(String(32), nullable=False)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    context_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
