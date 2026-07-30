"""Tenant ↔ IdP issuer federation bindings — memory|sql (PHX-G66/G67/G78)."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, replace
from typing import Any, Literal
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from kernel.infrastructure.persistence.session import create_session_factory
from kernel.infrastructure.persistence.tenant_idp_models import (
    DEFAULT_PRIORITY,
    TenantIdpBindingRecord,
)
from kernel.infrastructure.persistence.tenant_idp_repository import (
    SQLAlchemyTenantIdpRepository,
)

StoreKind = Literal["memory", "sql"]


@dataclass(slots=True)
class TenantIdpBinding:
    id: UUID
    tenant_id: UUID
    issuer: str
    status: str
    priority: int
    created_at: float
    updated_at: float
    version: int


_BINDINGS: dict[UUID, TenantIdpBinding] = {}
_ENFORCE_OVERRIDE: bool | None = None
_STORE_OVERRIDE: StoreKind | None = None
_SESSION_FACTORY: sessionmaker[Session] | None = None
_SQL_REPO: SQLAlchemyTenantIdpRepository | None = None


def configure_tenant_idp_federation(
    *,
    enforce: bool | None = None,
    store: StoreKind | None = None,
    session_factory: sessionmaker[Session] | None = None,
) -> None:
    global _ENFORCE_OVERRIDE, _STORE_OVERRIDE, _SESSION_FACTORY, _SQL_REPO
    _ENFORCE_OVERRIDE = enforce
    _STORE_OVERRIDE = store
    _SESSION_FACTORY = session_factory
    _SQL_REPO = None
    _BINDINGS.clear()


def clear_tenant_idp_federation() -> None:
    _BINDINGS.clear()
    global _SQL_REPO
    if federation_store_kind() == "sql":
        try:
            _sql_repo().clear()
        except RuntimeError:
            pass
    _SQL_REPO = None


def tenant_idp_federation_enabled() -> bool:
    if _ENFORCE_OVERRIDE is not None:
        return _ENFORCE_OVERRIDE
    raw = (os.environ.get("EAOS_TENANT_IDP_FEDERATION") or "0").strip().lower()
    return raw in ("1", "true", "yes", "on")


def federation_store_kind() -> StoreKind:
    if _STORE_OVERRIDE is not None:
        return _STORE_OVERRIDE
    raw = (os.environ.get("EAOS_TENANT_IDP_FEDERATION_STORE") or "memory").strip().lower()
    if raw in ("", "memory"):
        return "memory"
    if raw == "sql":
        return "sql"
    raise RuntimeError("EAOS_TENANT_IDP_FEDERATION_STORE must be memory or sql")


def federation_store_label() -> str:
    return "process_memory" if federation_store_kind() == "memory" else "sql"


def list_tenant_idp_bindings(
    *,
    tenant_id: UUID | None = None,
    include_disabled: bool = True,
) -> list[TenantIdpBinding]:
    if federation_store_kind() == "sql":
        try:
            rows = _sql_repo().list_all(
                tenant_id=tenant_id, include_disabled=include_disabled
            )
        except RuntimeError as exc:
            raise _unavailable(exc) from exc
        return [_from_sql(row) for row in rows]
    rows = list(_BINDINGS.values())
    if tenant_id is not None:
        rows = [row for row in rows if row.tenant_id == tenant_id]
    if not include_disabled:
        rows = [row for row in rows if row.status == "active"]
    return sorted(
        rows,
        key=lambda row: (str(row.tenant_id), row.priority, row.issuer.casefold()),
    )


def get_tenant_idp_binding(binding_id: UUID) -> TenantIdpBinding | None:
    if federation_store_kind() == "sql":
        try:
            row = _sql_repo().get(binding_id)
        except RuntimeError as exc:
            raise _unavailable(exc) from exc
        return None if row is None else _from_sql(row)
    return _BINDINGS.get(binding_id)


def create_tenant_idp_binding(*, tenant_id: UUID, issuer: str) -> TenantIdpBinding:
    normalized = _normalize_issuer(issuer)
    if federation_store_kind() == "sql":
        try:
            row, _action = _sql_repo().create_or_reactivate(
                tenant_id=tenant_id,
                issuer=normalized,
            )
        except ValueError as exc:
            if str(exc) == "active_exists":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "code": "GATEWAY_TENANT_IDP_BINDING_EXISTS",
                        "message": "active binding already exists for tenant and issuer",
                    },
                ) from exc
            raise
        except RuntimeError as exc:
            raise _unavailable(exc) from exc
        return _from_sql(row)

    for row in _BINDINGS.values():
        if (
            row.tenant_id == tenant_id
            and row.issuer.casefold() == normalized.casefold()
            and row.status == "active"
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "GATEWAY_TENANT_IDP_BINDING_EXISTS",
                    "message": "active binding already exists for tenant and issuer",
                },
            )
        if (
            row.tenant_id == tenant_id
            and row.issuer.casefold() == normalized.casefold()
            and row.status == "disabled"
        ):
            updated = replace(
                row,
                issuer=normalized,
                status="active",
                updated_at=time.time(),
                version=row.version + 1,
            )
            _BINDINGS[row.id] = updated
            return updated
    now = time.time()
    record = TenantIdpBinding(
        id=uuid4(),
        tenant_id=tenant_id,
        issuer=normalized,
        status="active",
        priority=DEFAULT_PRIORITY,
        created_at=now,
        updated_at=now,
        version=1,
    )
    _BINDINGS[record.id] = record
    return record


def set_tenant_idp_binding_priority(
    binding_id: UUID, *, priority: int
) -> TenantIdpBinding:
    if not isinstance(priority, int) or isinstance(priority, bool) or priority < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "GATEWAY_TENANT_IDP_PRIORITY_INVALID",
                "message": "priority must be an integer >= 0",
            },
        )
    if federation_store_kind() == "sql":
        try:
            row = _sql_repo().set_priority(binding_id, priority=priority)
        except RuntimeError as exc:
            raise _unavailable(exc) from exc
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "GATEWAY_TENANT_IDP_BINDING_NOT_FOUND",
                    "message": "federation binding not found",
                },
            )
        return _from_sql(row)

    record = _BINDINGS.get(binding_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "GATEWAY_TENANT_IDP_BINDING_NOT_FOUND",
                "message": "federation binding not found",
            },
        )
    updated = replace(
        record,
        priority=priority,
        updated_at=time.time(),
        version=record.version + 1,
    )
    _BINDINGS[binding_id] = updated
    return updated


def preferred_active_issuer(tenant_id: UUID) -> str | None:
    """Lowest priority among active bindings for tenant (read helper; PHX-G78)."""

    rows = [
        row
        for row in list_tenant_idp_bindings(tenant_id=tenant_id, include_disabled=False)
        if row.status == "active"
    ]
    if not rows:
        return None
    return rows[0].issuer


def unbind_tenant_idp_binding(binding_id: UUID) -> TenantIdpBinding:
    if federation_store_kind() == "sql":
        try:
            row = _sql_repo().disable(binding_id)
        except RuntimeError as exc:
            raise _unavailable(exc) from exc
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "GATEWAY_TENANT_IDP_BINDING_NOT_FOUND",
                    "message": "federation binding not found",
                },
            )
        return _from_sql(row)

    record = _BINDINGS.get(binding_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "GATEWAY_TENANT_IDP_BINDING_NOT_FOUND",
                "message": "federation binding not found",
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
    _BINDINGS[binding_id] = updated
    return updated


def resolve_federation_issuer(
    claims: dict[str, Any],
    *,
    eaos_jwt_issuer: str | None = None,
) -> str | None:
    """Pick IdP issuer for federation checks (PHX-G68)."""

    oidc = claims.get("eaos_oidc_issuer")
    if oidc is not None and str(oidc).strip():
        return str(oidc).strip().rstrip("/")
    iss = claims.get("iss")
    if iss is None or str(iss).strip() == "":
        return None
    cleaned = str(iss).strip().rstrip("/")
    if eaos_jwt_issuer and cleaned.casefold() == eaos_jwt_issuer.strip().rstrip("/").casefold():
        # EAOS-minted token without OIDC provenance cannot satisfy federation.
        return None
    return cleaned


def assert_tenant_idp_binding(*, tenant_id: str | UUID, issuer: str | None) -> None:
    """Fail-closed when federation enforcement is on."""

    if not tenant_idp_federation_enabled():
        return
    if issuer is None or str(issuer).strip() == "":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "GATEWAY_TENANT_IDP_FEDERATION_DENIED",
                "message": "IdP issuer provenance required when tenant IdP federation is enabled",
            },
        )
    tenant = UUID(str(tenant_id))
    needle = _normalize_issuer(issuer)
    if federation_store_kind() == "sql":
        try:
            ok = _sql_repo().has_active(tenant_id=tenant, issuer=needle)
        except RuntimeError as exc:
            raise _unavailable(exc) from exc
        if ok:
            return
    else:
        for row in _BINDINGS.values():
            if (
                row.tenant_id == tenant
                and row.status == "active"
                and row.issuer.casefold() == needle.casefold()
            ):
                return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "code": "GATEWAY_TENANT_IDP_FEDERATION_DENIED",
            "message": "no active tenant IdP federation binding for issuer",
        },
    )


def serialize_tenant_idp_binding(row: TenantIdpBinding) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "bound_tenant_id": str(row.tenant_id),
        "issuer": row.issuer,
        "status": row.status,
        "priority": row.priority,
        "version": row.version,
    }


def federation_matrix(
    *,
    include_unbound_issuers: bool = True,
) -> dict[str, Any]:
    """Platform-plane tenant × issuer matrix over existing bindings (PHX-G77)."""

    from api.gateway.idp_registry import list_idp_issuers

    bindings = list_tenant_idp_bindings(include_disabled=True)
    registry_rows = list_idp_issuers(include_disabled=True)
    registry_by_issuer = {row.issuer.rstrip("/"): row for row in registry_rows}

    cells: list[dict[str, Any]] = []
    tenant_ids: set[str] = set()
    issuers: set[str] = set()
    bound_pairs: set[tuple[str, str]] = set()

    for row in bindings:
        tenant_key = str(row.tenant_id)
        issuer_key = row.issuer.rstrip("/")
        tenant_ids.add(tenant_key)
        issuers.add(issuer_key)
        bound_pairs.add((tenant_key, issuer_key))
        reg = registry_by_issuer.get(issuer_key)
        cells.append(
            {
                "bound_tenant_id": tenant_key,
                "issuer": row.issuer,
                "state": "active" if row.status == "active" else "disabled",
                "binding_id": str(row.id),
                "priority": row.priority,
                "registry_status": (
                    "absent" if reg is None else ("active" if reg.status == "active" else "disabled")
                ),
            }
        )

    if include_unbound_issuers:
        for reg in registry_rows:
            issuer_key = reg.issuer.rstrip("/")
            issuers.add(issuer_key)
            # Issuer-level unbound cell (no tenant) when never bound to any tenant.
            if not any(pair[1] == issuer_key for pair in bound_pairs):
                cells.append(
                    {
                        "bound_tenant_id": None,
                        "issuer": reg.issuer,
                        "state": "unbound",
                        "binding_id": None,
                        "priority": None,
                        "registry_status": (
                            "active" if reg.status == "active" else "disabled"
                        ),
                    }
                )

    cells.sort(
        key=lambda cell: (
            cell["bound_tenant_id"] or "",
            cell["priority"] if cell["priority"] is not None else 10**9,
            str(cell["issuer"]).casefold(),
        )
    )
    return {
        "cells": cells,
        "tenants": sorted(tenant_ids),
        "issuers": sorted(issuers, key=str.casefold),
        "meta": {
            "cell_count": len(cells),
            "tenant_count": len(tenant_ids),
            "issuer_count": len(issuers),
            "binding_count": len(bindings),
            "active_count": sum(1 for row in bindings if row.status == "active"),
            "include_unbound_issuers": include_unbound_issuers,
        },
    }


def federation_status_view() -> dict[str, Any]:
    planes = ["oidc", "jwt"]
    try:
        kind = federation_store_kind()
        rows = list_tenant_idp_bindings(include_disabled=True)
        matrix = federation_matrix(include_unbound_issuers=True)
    except RuntimeError as exc:
        return {
            "enabled": tenant_idp_federation_enabled(),
            "store": "unavailable",
            "error": str(exc),
            "planes": planes,
            "binding_count": 0,
            "active_count": 0,
            "matrix": {
                "cell_count": 0,
                "tenant_count": 0,
                "issuer_count": 0,
            },
        }
    store_label = "process_memory" if kind == "memory" else "sql"
    return {
        "enabled": tenant_idp_federation_enabled(),
        "store": store_label,
        "planes": planes,
        "binding_count": len(rows),
        "active_count": sum(1 for row in rows if row.status == "active"),
        "matrix": {
            "cell_count": matrix["meta"]["cell_count"],
            "tenant_count": matrix["meta"]["tenant_count"],
            "issuer_count": matrix["meta"]["issuer_count"],
        },
    }


def _normalize_issuer(issuer: str) -> str:
    cleaned = (issuer or "").strip().rstrip("/")
    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "GATEWAY_TENANT_IDP_BINDING_INVALID",
                "message": "issuer is required",
            },
        )
    if "://" not in cleaned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "GATEWAY_TENANT_IDP_BINDING_INVALID",
                "message": "issuer must be an absolute URI",
            },
        )
    return cleaned


def _from_sql(row: TenantIdpBindingRecord) -> TenantIdpBinding:
    return TenantIdpBinding(
        id=row.id,
        tenant_id=row.tenant_id,
        issuer=row.issuer,
        status=row.status,
        priority=int(row.priority),
        created_at=row.created_at.timestamp(),
        updated_at=row.updated_at.timestamp(),
        version=int(row.version),
    )


def _unavailable(exc: Exception) -> RuntimeError:
    return RuntimeError(
        "EAOS_TENANT_IDP_FEDERATION_STORE=sql requires EAOS_DATABASE_URL (postgresql+psycopg)"
    )


def _sql_repo() -> SQLAlchemyTenantIdpRepository:
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
        raise _unavailable(exc) from exc
    _SQL_REPO = SQLAlchemyTenantIdpRepository(factory)
    return _SQL_REPO
