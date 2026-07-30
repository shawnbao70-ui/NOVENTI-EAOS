"""Platform IdP issuer registry + tenant federation bindings/matrix (PHX-G56/G57/G66/G77)."""

from __future__ import annotations

import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from api.gateway.context import derive_platform_context, reject_context_override
from api.gateway.idp_registry import (
    create_idp_issuer,
    disable_idp_issuer,
    list_idp_issuers,
    serialize_idp_issuer,
)
from api.gateway.oidc import maybe_write_discovery_to_registry
from api.gateway.schemas.platform import (
    CreateIdpIssuerRequest,
    CreateTenantIdpBindingRequest,
    DiscoverySyncEnvelope,
    EmptyBody,
    FederationMatrixEnvelope,
    IdpIssuerEnvelope,
    IdpIssuerListEnvelope,
    SetBindingPriorityRequest,
    TenantIdpBindingEnvelope,
    TenantIdpBindingListEnvelope,
)
from api.gateway.tenant_idp_federation import (
    create_tenant_idp_binding,
    federation_matrix,
    list_tenant_idp_bindings,
    serialize_tenant_idp_binding,
    set_tenant_idp_binding_priority,
    unbind_tenant_idp_binding,
)
from kernel.shared.context import ExecutionContext

router = APIRouter(prefix="/v1/platform/idp", tags=["Platform IdP"])


@router.get("/issuers", response_model=IdpIssuerListEnvelope)
def list_issuers(
    ctx: ExecutionContext = Depends(derive_platform_context),
) -> IdpIssuerListEnvelope:
    _ = ctx
    try:
        rows = list_idp_issuers(include_disabled=True)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_IDP_REGISTRY_UNAVAILABLE",
                "message": str(exc),
            },
        ) from exc
    items = [serialize_idp_issuer(row) for row in rows]
    return IdpIssuerListEnvelope.model_validate(
        {"data": items, "meta": {"count": len(items)}}
    )


@router.post(
    "/issuers",
    status_code=status.HTTP_201_CREATED,
    response_model=IdpIssuerEnvelope,
)
def create_issuer(
    body: CreateIdpIssuerRequest,
    ctx: ExecutionContext = Depends(derive_platform_context),
) -> IdpIssuerEnvelope:
    _ = ctx
    reject_context_override(body.model_dump(exclude_none=True))
    raw_jwks = body.jwks_json
    if isinstance(raw_jwks, dict):
        jwks_json = json.dumps(raw_jwks)
    elif raw_jwks is None:
        jwks_json = None
    else:
        jwks_json = str(raw_jwks)
    record = create_idp_issuer(
        issuer=body.issuer,
        jwks_url=body.jwks_url,
        jwks_json=jwks_json,
    )
    return IdpIssuerEnvelope.model_validate({"data": serialize_idp_issuer(record)})


@router.post("/issuers/{issuer_id}/disable", response_model=IdpIssuerEnvelope)
def disable_issuer(
    issuer_id: UUID,
    body: EmptyBody | None = None,
    ctx: ExecutionContext = Depends(derive_platform_context),
) -> IdpIssuerEnvelope:
    _ = ctx
    payload = body or EmptyBody()
    reject_context_override(payload.model_dump())
    record = disable_idp_issuer(issuer_id)
    return IdpIssuerEnvelope.model_validate({"data": serialize_idp_issuer(record)})


@router.post("/discovery/sync", response_model=DiscoverySyncEnvelope)
def sync_discovery_to_registry(
    body: EmptyBody | None = None,
    ctx: ExecutionContext = Depends(derive_platform_context),
) -> DiscoverySyncEnvelope:
    """Force Discovery → registry upsert when EAOS_OIDC_DISCOVERY_REGISTRY_WRITE is on."""

    _ = ctx
    payload = body or EmptyBody()
    reject_context_override(payload.model_dump())
    result = maybe_write_discovery_to_registry(raise_on_error=True)
    return DiscoverySyncEnvelope.model_validate({"data": result})


@router.get("/federation/matrix", response_model=FederationMatrixEnvelope)
def get_federation_matrix(
    include_unbound_issuers: bool = True,
    ctx: ExecutionContext = Depends(derive_platform_context),
) -> FederationMatrixEnvelope:
    """Cross-tenant tenant×issuer matrix (PHX-G77); read-only."""

    _ = ctx
    try:
        matrix = federation_matrix(include_unbound_issuers=include_unbound_issuers)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_TENANT_IDP_FEDERATION_UNAVAILABLE",
                "message": str(exc),
            },
        ) from exc
    return FederationMatrixEnvelope.model_validate(
        {
            "data": {
                "cells": matrix["cells"],
                "tenants": matrix["tenants"],
                "issuers": matrix["issuers"],
            },
            "meta": matrix["meta"],
        }
    )


@router.get(
    "/federation/tenants/{tenant_id}/bindings",
    response_model=TenantIdpBindingListEnvelope,
)
def list_federation_bindings(
    tenant_id: UUID,
    ctx: ExecutionContext = Depends(derive_platform_context),
) -> TenantIdpBindingListEnvelope:
    _ = ctx
    try:
        rows = list_tenant_idp_bindings(tenant_id=tenant_id, include_disabled=True)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_TENANT_IDP_FEDERATION_UNAVAILABLE",
                "message": str(exc),
            },
        ) from exc
    items = [serialize_tenant_idp_binding(row) for row in rows]
    return TenantIdpBindingListEnvelope.model_validate(
        {"data": items, "meta": {"count": len(items)}}
    )


@router.post(
    "/federation/tenants/{tenant_id}/bindings",
    status_code=status.HTTP_201_CREATED,
    response_model=TenantIdpBindingEnvelope,
)
def create_federation_binding(
    tenant_id: UUID,
    body: CreateTenantIdpBindingRequest,
    ctx: ExecutionContext = Depends(derive_platform_context),
) -> TenantIdpBindingEnvelope:
    _ = ctx
    reject_context_override(body.model_dump())
    try:
        record = create_tenant_idp_binding(
            tenant_id=tenant_id,
            issuer=body.issuer,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_TENANT_IDP_FEDERATION_UNAVAILABLE",
                "message": str(exc),
            },
        ) from exc
    return TenantIdpBindingEnvelope.model_validate(
        {"data": serialize_tenant_idp_binding(record)}
    )


@router.post(
    "/federation/bindings/{binding_id}/unbind",
    response_model=TenantIdpBindingEnvelope,
)
def unbind_federation_binding(
    binding_id: UUID,
    body: EmptyBody | None = None,
    ctx: ExecutionContext = Depends(derive_platform_context),
) -> TenantIdpBindingEnvelope:
    _ = ctx
    payload = body or EmptyBody()
    reject_context_override(payload.model_dump())
    try:
        record = unbind_tenant_idp_binding(binding_id)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_TENANT_IDP_FEDERATION_UNAVAILABLE",
                "message": str(exc),
            },
        ) from exc
    return TenantIdpBindingEnvelope.model_validate(
        {"data": serialize_tenant_idp_binding(record)}
    )


@router.post(
    "/federation/bindings/{binding_id}/priority",
    response_model=TenantIdpBindingEnvelope,
)
def set_federation_binding_priority(
    binding_id: UUID,
    body: SetBindingPriorityRequest,
    ctx: ExecutionContext = Depends(derive_platform_context),
) -> TenantIdpBindingEnvelope:
    """Set issuer priority on a binding (PHX-G78); lower wins."""

    _ = ctx
    reject_context_override(body.model_dump())
    try:
        record = set_tenant_idp_binding_priority(binding_id, priority=body.priority)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_TENANT_IDP_FEDERATION_UNAVAILABLE",
                "message": str(exc),
            },
        ) from exc
    return TenantIdpBindingEnvelope.model_validate(
        {"data": serialize_tenant_idp_binding(record)}
    )
