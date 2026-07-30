"""PostgreSQL Engine and Session factories."""

from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from kernel.infrastructure.persistence.configuration import database_url_from_environment


def create_postgresql_engine() -> Engine:
    """Create the approved production Engine without opening a connection."""
    return create_engine(
        database_url_from_environment(),
        pool_pre_ping=True,
    )


def create_session_factory(
    engine: Engine | None = None,
) -> sessionmaker[Session]:
    """Create explicit, non-autocommit Sessions for Kernel commands."""
    return sessionmaker(
        bind=engine if engine is not None else create_postgresql_engine(),
        class_=Session,
        autoflush=False,
        expire_on_commit=False,
    )
