"""Platform declared EAOS roles catalog (PHX-G90)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from api.gateway.context import derive_platform_context, reject_context_override
from api.gateway.role_catalog_store import (
    disable_declared_role,
    list_declared_roles,
    serialize_declared_role,
    upsert_declared_role,
)
from api.gateway.schemas.platform import (
    DeclaredRoleActionEnvelope,
    DeclaredRoleEnvelope,
    DeclaredRoleListEnvelope,
    EmptyBody,
    UpsertDeclaredRoleRequest,
)
from kernel.shared.context import ExecutionContext

router = APIRouter(prefix="/v1/platform/roles", tags=["Platform Roles"])


@router.get("", response_model=DeclaredRoleListEnvelope)
def list_roles(
    ctx: ExecutionContext = Depends(derive_platform_context),
) -> DeclaredRoleListEnvelope:
    _ = ctx
    try:
        rows = list_declared_roles(include_disabled=True)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_ROLE_CATALOG_UNAVAILABLE",
                "message": str(exc),
            },
        ) from exc
    items = [serialize_declared_role(row) for row in rows]
    return DeclaredRoleListEnvelope.model_validate(
        {"data": items, "meta": {"count": len(items)}}
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=DeclaredRoleActionEnvelope,
)
def upsert_role(
    body: UpsertDeclaredRoleRequest,
    ctx: ExecutionContext = Depends(derive_platform_context),
) -> DeclaredRoleActionEnvelope:
    _ = ctx
    reject_context_override(body.model_dump())
    record, action = upsert_declared_role(name=body.name)
    payload = serialize_declared_role(record)
    payload["action"] = action
    return DeclaredRoleActionEnvelope.model_validate({"data": payload})


@router.post("/{role_id}/disable", response_model=DeclaredRoleEnvelope)
def disable_role(
    role_id: UUID,
    body: EmptyBody | None = None,
    ctx: ExecutionContext = Depends(derive_platform_context),
) -> DeclaredRoleEnvelope:
    _ = ctx
    payload = body or EmptyBody()
    reject_context_override(payload.model_dump())
    record = disable_declared_role(role_id)
    return DeclaredRoleEnvelope.model_validate(
        {"data": serialize_declared_role(record)}
    )
