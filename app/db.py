"""Database setup helpers."""

from __future__ import annotations

from sqlalchemy import create_engine

from app.models import Base


def init_engine(sqlite_path: str):
    return create_engine(f"sqlite:///{sqlite_path}", future=True)


def create_schema(engine) -> None:
    """Scaffold approach: create tables from metadata directly."""
    Base.metadata.create_all(engine)
