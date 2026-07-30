"""IdP issuer registry with memory/SQL stores (PHX-G56/G57 Foundation)."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, replace
from typing import Any, Literal
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlalchemy.orm import Session, sessionmaker

from api.gateway.auth_jwt import JwtIssuerBinding, JwtSettings
from kernel.infrastructure.persistence.idp_issuer_models import IdpIssuerBindingRecord
from kernel.infrastructure.persistence.idp_issuer_repository import (
    SQLAlchemyIdpIssuerRepository,
    decode_jwks_json,
)
from kernel.infrastructure.persistence.session import create_session_factory

StoreKind = Literal["memory", "sql"]


@dataclass(slots=True)
class IdpIssuerRecord:
    id: UUID
    issuer: str
    jwks_url: str | None
    jwks_json: str | None
    status: str
    created_at: float
    updated_at: float
    version: int


_REGISTRY: dict[UUID, IdpIssuerRecord] = {}
_STORE_OVERRIDE: StoreKind | None = None
_SESSION_FACTORY: sessionmaker[Session] | None = None
_SQL_REPO: SQLAlchemyIdpIssuerRepository | None = None


def configure_idp_registry(
    *,
    store: StoreKind | None = None,
    session_factory: sessionmaker[Session] | None = None,
) -> None:
    """Test/prod override for registry backend (None = read env)."""

    global _STORE_OVERRIDE, _SESSION_FACTORY, _SQL_REPO
    _STORE_OVERRIDE = store
    _SESSION_FACTORY = session_factory
    _SQL_REPO = None
    _REGISTRY.clear()


def clear_idp_registry() -> None:
    _REGISTRY.clear()
    global _SQL_REPO
    if _SESSION_FACTORY is not None:
        with _SESSION_FACTORY() as session:
            session.execute(delete(IdpIssuerBindingRecord))
            session.commit()
    _SQL_REPO = None
    from api.gateway.oidc import clear_discovery_registry_write_state

    clear_discovery_registry_write_state()


def registry_store_kind() -> StoreKind:
    if _STORE_OVERRIDE is not None:
        return _STORE_OVERRIDE
    raw = (os.environ.get("EAOS_IDP_REGISTRY_STORE") or "memory").strip().lower()
    if raw in ("", "memory"):
        return "memory"
    if raw == "sql":
        return "sql"
    raise RuntimeError("EAOS_IDP_REGISTRY_STORE must be memory or sql")


def list_idp_issuers(*, include_disabled: bool = True) -> list[IdpIssuerRecord]:
    if registry_store_kind() == "sql":
        try:
            rows = _sql_repo().list_all(include_disabled=include_disabled)
        except RuntimeError as exc:
            raise RuntimeError(
                "EAOS_IDP_REGISTRY_STORE=sql requires EAOS_DATABASE_URL (postgresql+psycopg)"
            ) from exc
        return [_from_sql(row) for row in rows]
    rows = list(_REGISTRY.values())
    if not include_disabled:
        rows = [row for row in rows if row.status == "active"]
    return sorted(rows, key=lambda row: row.issuer.casefold())


def get_idp_issuer(issuer_id: UUID) -> IdpIssuerRecord | None:
    if registry_store_kind() == "sql":
        try:
            row = _sql_repo().get(issuer_id)
        except RuntimeError as exc:
            raise RuntimeError(
                "EAOS_IDP_REGISTRY_STORE=sql requires EAOS_DATABASE_URL (postgresql+psycopg)"
            ) from exc
        return None if row is None else _from_sql(row)
    return _REGISTRY.get(issuer_id)


def create_idp_issuer(
    *,
    issuer: str,
    jwks_url: str | None,
    jwks_json: str | None,
) -> IdpIssuerRecord:
    normalized = _normalize_issuer(issuer)
    _require_jwks(jwks_url=jwks_url, jwks_json=jwks_json)
    clean_url = (jwks_url or "").strip() or None
    clean_json = (jwks_json or "").strip() or None

    if registry_store_kind() == "sql":
        try:
            row, _action = _sql_repo().create_or_reactivate(
                issuer=normalized,
                jwks_url=clean_url,
                jwks_json=clean_json,
            )
        except ValueError as exc:
            if str(exc) == "active_exists":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "code": "GATEWAY_IDP_ISSUER_EXISTS",
                        "message": "an active registry issuer already exists for this issuer",
                    },
                ) from exc
            raise
        except RuntimeError as exc:
            raise _unavailable(exc) from exc
        return _from_sql(row)

    for existing in _REGISTRY.values():
        if existing.issuer.casefold() == normalized.casefold() and existing.status == "active":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "GATEWAY_IDP_ISSUER_EXISTS",
                    "message": "an active registry issuer already exists for this issuer",
                },
            )
    now = time.time()
    record = IdpIssuerRecord(
        id=uuid4(),
        issuer=normalized,
        jwks_url=clean_url,
        jwks_json=clean_json,
        status="active",
        created_at=now,
        updated_at=now,
        version=1,
    )
    _REGISTRY[record.id] = record
    return record


def upsert_idp_issuer(
    *,
    issuer: str,
    jwks_url: str | None,
    jwks_json: str | None,
) -> tuple[IdpIssuerRecord, str]:
    """Create or update registry row for Discovery writeback (PHX-G60)."""

    normalized = _normalize_issuer(issuer)
    _require_jwks(jwks_url=jwks_url, jwks_json=jwks_json)
    clean_url = (jwks_url or "").strip() or None
    clean_json = (jwks_json or "").strip() or None

    if registry_store_kind() == "sql":
        try:
            row, action = _sql_repo().upsert(
                issuer=normalized,
                jwks_url=clean_url,
                jwks_json=clean_json,
            )
        except RuntimeError as exc:
            raise _unavailable(exc) from exc
        return _from_sql(row), action

    for existing in _REGISTRY.values():
        if existing.issuer.casefold() != normalized.casefold():
            continue
        same = (
            existing.status == "active"
            and existing.jwks_url == clean_url
            and existing.jwks_json == clean_json
        )
        if same:
            return existing, "unchanged"
        prior = existing.status
        updated = replace(
            existing,
            jwks_url=clean_url,
            jwks_json=clean_json,
            status="active",
            updated_at=time.time(),
            version=existing.version + 1,
        )
        _REGISTRY[existing.id] = updated
        return updated, "reactivated" if prior == "disabled" else "updated"

    now = time.time()
    record = IdpIssuerRecord(
        id=uuid4(),
        issuer=normalized,
        jwks_url=clean_url,
        jwks_json=clean_json,
        status="active",
        created_at=now,
        updated_at=now,
        version=1,
    )
    _REGISTRY[record.id] = record
    return record, "created"


def disable_idp_issuer(issuer_id: UUID) -> IdpIssuerRecord:
    if registry_store_kind() == "sql":
        try:
            row = _sql_repo().disable(issuer_id)
        except RuntimeError as exc:
            raise _unavailable(exc) from exc
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "GATEWAY_IDP_ISSUER_NOT_FOUND",
                    "message": "idp issuer registry entry not found",
                },
            )
        return _from_sql(row)

    record = _REGISTRY.get(issuer_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "GATEWAY_IDP_ISSUER_NOT_FOUND",
                "message": "idp issuer registry entry not found",
            },
        )
    if record.status == "disabled":
        return record
    updated = replace(
        record,
        status="disabled",
        updated_at=time.time(),
        version=record.version + 1,
    )
    _REGISTRY[issuer_id] = updated
    return updated


def merge_registry_issuers(settings: JwtSettings) -> JwtSettings:
    """Merge active registry bindings; env issuers win on issuer clash."""

    try:
        active = list_idp_issuers(include_disabled=False)
    except RuntimeError:
        return settings
    if not active:
        return settings

    base: list[JwtIssuerBinding] = list(settings.issuers)
    if not base and settings.issuer and (settings.jwks_url or settings.jwks_json):
        base.append(
            JwtIssuerBinding(
                issuer=settings.issuer,
                jwks_url=settings.jwks_url,
                jwks_json=settings.jwks_json,
            )
        )
    claimed = {binding.issuer.casefold() for binding in base}
    extras: list[JwtIssuerBinding] = []
    for record in active:
        if record.issuer.casefold() in claimed:
            continue
        extras.append(
            JwtIssuerBinding(
                issuer=record.issuer,
                jwks_url=record.jwks_url,
                jwks_json=record.jwks_json,
            )
        )
        claimed.add(record.issuer.casefold())
    if not extras:
        if base and not settings.issuers:
            return _with_issuers(settings, tuple(base))
        return settings
    return _with_issuers(settings, tuple(base) + tuple(extras))


def registry_status_view() -> dict[str, Any]:
    try:
        kind = registry_store_kind()
        rows = list_idp_issuers(include_disabled=True)
    except RuntimeError as exc:
        return {
            "writable": True,
            "store": "unavailable",
            "error": str(exc),
            "issuers": [],
        }
    store_label = "process_memory" if kind == "memory" else "sql"
    return {
        "writable": True,
        "store": store_label,
        "issuers": [
            {
                "id": str(row.id),
                "issuer": row.issuer,
                "jwks_url": row.jwks_url,
                "has_jwks_json": bool(row.jwks_json),
                "status": row.status,
                "version": row.version,
            }
            for row in rows
        ],
    }


def serialize_idp_issuer(record: IdpIssuerRecord) -> dict[str, Any]:
    return {
        "id": str(record.id),
        "issuer": record.issuer,
        "jwks_url": record.jwks_url,
        "has_jwks_json": bool(record.jwks_json),
        "status": record.status,
        "version": record.version,
    }


def _sql_repo() -> SQLAlchemyIdpIssuerRepository:
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
            "EAOS_IDP_REGISTRY_STORE=sql requires EAOS_DATABASE_URL (postgresql+psycopg)"
        ) from exc
    _SQL_REPO = SQLAlchemyIdpIssuerRepository(factory)
    return _SQL_REPO


def _from_sql(row: IdpIssuerBindingRecord) -> IdpIssuerRecord:
    return IdpIssuerRecord(
        id=row.id,
        issuer=row.issuer,
        jwks_url=row.jwks_url,
        jwks_json=decode_jwks_json(row.jwks_json),
        status=row.status,
        created_at=row.created_at.timestamp(),
        updated_at=row.updated_at.timestamp(),
        version=int(row.version),
    )


def _unavailable(exc: RuntimeError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "code": "GATEWAY_IDP_REGISTRY_UNAVAILABLE",
            "message": str(exc),
        },
    )


def _with_issuers(settings: JwtSettings, issuers: tuple[JwtIssuerBinding, ...]) -> JwtSettings:
    return JwtSettings(
        secret=settings.secret,
        issuer=settings.issuer,
        audience=settings.audience,
        allow_dev_headers=settings.allow_dev_headers,
        require_jwt=settings.require_jwt,
        jwks_json=settings.jwks_json,
        jwks_url=settings.jwks_url,
        leeway_seconds=settings.leeway_seconds,
        jwks_cache_seconds=settings.jwks_cache_seconds,
        issuers=issuers,
        denylist_json=settings.denylist_json,
        denylist_url=settings.denylist_url,
        denylist_cache_seconds=settings.denylist_cache_seconds,
    )


def _normalize_issuer(issuer: str) -> str:
    value = (issuer or "").strip()
    if not value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "GATEWAY_IDP_INVALID",
                "message": "issuer is required",
            },
        )
    return value


def _require_jwks(*, jwks_url: str | None, jwks_json: str | None) -> None:
    if (jwks_url or "").strip() or (jwks_json or "").strip():
        return
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "code": "GATEWAY_IDP_INVALID",
            "message": "jwks_url or jwks_json is required",
        },
    )
