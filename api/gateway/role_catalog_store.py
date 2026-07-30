"""Declared EAOS roles catalog store — memory|sql (PHX-G90 / ADR-0109)."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, replace
from typing import Literal
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from kernel.infrastructure.persistence.eaos_declared_role_models import (
    EaosDeclaredRoleRecord,
)
from kernel.infrastructure.persistence.eaos_declared_role_repository import (
    SQLAlchemyEaosDeclaredRoleRepository,
)
from kernel.infrastructure.persistence.session import create_session_factory

StoreKind = Literal["memory", "sql"]


@dataclass(slots=True)
class DeclaredRoleRecord:
    id: UUID
    name: str
    status: str
    created_at: float
    updated_at: float
    version: int


_STORE: dict[UUID, DeclaredRoleRecord] = {}
_STORE_OVERRIDE: StoreKind | None = None
_SESSION_FACTORY: sessionmaker[Session] | None = None
_SQL_REPO: SQLAlchemyEaosDeclaredRoleRepository | None = None


def configure_role_catalog_store(
    *,
    store: StoreKind | None = None,
    session_factory: sessionmaker[Session] | None = None,
) -> None:
    global _STORE_OVERRIDE, _SESSION_FACTORY, _SQL_REPO
    _STORE_OVERRIDE = store
    _SESSION_FACTORY = session_factory
    _SQL_REPO = None
    _STORE.clear()


def clear_role_catalog_store() -> None:
    _STORE.clear()
    global _SQL_REPO
    if role_catalog_store_kind() == "sql":
        try:
            _sql_repo().clear()
        except RuntimeError:
            pass
    _SQL_REPO = None


def role_catalog_store_kind() -> StoreKind:
    if _STORE_OVERRIDE is not None:
        return _STORE_OVERRIDE
    raw = (os.environ.get("EAOS_ROLE_CATALOG_STORE") or "memory").strip().lower()
    if raw in ("", "memory"):
        return "memory"
    if raw == "sql":
        return "sql"
    raise RuntimeError("EAOS_ROLE_CATALOG_STORE must be memory or sql")


def role_catalog_store_label() -> str:
    return "process_memory" if role_catalog_store_kind() == "memory" else "sql"


def list_declared_roles(*, include_disabled: bool = True) -> list[DeclaredRoleRecord]:
    if role_catalog_store_kind() == "sql":
        try:
            rows = _sql_repo().list_all(include_disabled=include_disabled)
        except RuntimeError as exc:
            raise RuntimeError(
                "EAOS_ROLE_CATALOG_STORE=sql requires EAOS_DATABASE_URL (postgresql+psycopg)"
            ) from exc
        return [_from_sql(row) for row in rows]
    rows = list(_STORE.values())
    if not include_disabled:
        rows = [row for row in rows if row.status == "active"]
    return sorted(rows, key=lambda row: row.name.casefold())


def active_declared_role_names() -> list[str]:
    return [row.name for row in list_declared_roles(include_disabled=False)]


def upsert_declared_role(*, name: str) -> tuple[DeclaredRoleRecord, str]:
    normalized = _normalize_name(name)
    if role_catalog_store_kind() == "sql":
        try:
            row, action = _sql_repo().upsert(name=normalized)
        except RuntimeError as exc:
            raise _unavailable(exc) from exc
        return _from_sql(row), action

    now = time.time()
    for existing in _STORE.values():
        if existing.name.casefold() != normalized.casefold():
            continue
        if existing.status == "active":
            return existing, "unchanged"
        updated = replace(
            existing,
            status="active",
            updated_at=now,
            version=existing.version + 1,
        )
        _STORE[updated.id] = updated
        return updated, "reactivated"

    record = DeclaredRoleRecord(
        id=uuid4(),
        name=normalized,
        status="active",
        created_at=now,
        updated_at=now,
        version=1,
    )
    _STORE[record.id] = record
    return record, "created"


def disable_declared_role(role_id: UUID) -> DeclaredRoleRecord:
    if role_catalog_store_kind() == "sql":
        try:
            row = _sql_repo().disable(role_id)
        except RuntimeError as exc:
            raise _unavailable(exc) from exc
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "GATEWAY_ROLE_NOT_FOUND",
                    "message": "declared role not found",
                },
            )
        return _from_sql(row)

    existing = _STORE.get(role_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "GATEWAY_ROLE_NOT_FOUND",
                "message": "declared role not found",
            },
        )
    if existing.status == "disabled":
        return existing
    updated = replace(
        existing,
        status="disabled",
        updated_at=time.time(),
        version=existing.version + 1,
    )
    _STORE[role_id] = updated
    return updated


def serialize_declared_role(record: DeclaredRoleRecord) -> dict[str, object]:
    return {
        "id": str(record.id),
        "name": record.name,
        "status": record.status,
        "version": record.version,
    }


def _normalize_name(name: str) -> str:
    text = (name or "").strip()
    if not text or len(text) > 128:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "COMMON_VALIDATION_FAILED",
                "message": "role name is required and must be at most 128 characters",
            },
        )
    return text


def _sql_repo() -> SQLAlchemyEaosDeclaredRoleRepository:
    global _SQL_REPO
    if _SQL_REPO is not None:
        return _SQL_REPO
    try:
        factory = (
            _SESSION_FACTORY
            if _SESSION_FACTORY is not None
            else create_session_factory()
        )
    except RuntimeError as exc:
        raise RuntimeError(
            "EAOS_ROLE_CATALOG_STORE=sql requires EAOS_DATABASE_URL (postgresql+psycopg)"
        ) from exc
    _SQL_REPO = SQLAlchemyEaosDeclaredRoleRepository(factory)
    return _SQL_REPO


def _from_sql(row: EaosDeclaredRoleRecord) -> DeclaredRoleRecord:
    return DeclaredRoleRecord(
        id=row.id,
        name=row.name,
        status=row.status,
        created_at=row.created_at.timestamp(),
        updated_at=row.updated_at.timestamp(),
        version=int(row.version),
    )


def _unavailable(exc: RuntimeError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "code": "GATEWAY_ROLE_CATALOG_UNAVAILABLE",
            "message": str(exc),
        },
    )
