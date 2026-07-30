"""Fail-closed persistence configuration."""

from __future__ import annotations

import os

from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


def database_url_from_environment() -> str:
    """Return the approved PostgreSQL URL or fail before connecting."""
    database_url = os.getenv("EAOS_DATABASE_URL", "").strip()
    if not database_url:
        raise RuntimeError("EAOS_DATABASE_URL is required for database migrations")

    try:
        driver_name = make_url(database_url).drivername
    except ArgumentError as exc:
        raise RuntimeError("EAOS_DATABASE_URL is invalid") from exc
    if driver_name != "postgresql+psycopg":
        raise RuntimeError("EAOS_DATABASE_URL must use postgresql+psycopg")
    return database_url
