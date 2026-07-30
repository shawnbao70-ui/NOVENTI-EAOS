"""Trusted ExecutionContext derivation for the API gateway."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Annotated, Any
from uuid import UUID

from fastapi import Header, HTTPException, status

from api.gateway.auth_jwt import (
    JwtSettings,
    context_from_platform_claims,
    context_from_tenant_claims,
    extract_bearer,
    verify_token,
)
from api.gateway.idp_registry import merge_registry_issuers
from api.gateway.oidc import maybe_wire_discovery_jwks, maybe_write_discovery_to_registry
from kernel.shared.context import ExecutionContext, SubjectType


def _effective_jwt_settings(settings: JwtSettings) -> JwtSettings:
    maybe_write_discovery_to_registry(raise_on_error=True)
    return merge_registry_issuers(maybe_wire_discovery_jwks(settings))


_SUBJECT_HEADER = "X-EAOS-Subject-Id"
_SUBJECT_TYPE_HEADER = "X-EAOS-Subject-Type"
_TENANT_HEADER = "X-EAOS-Tenant-Id"
_CORRELATION_HEADER = "X-Correlation-Id"
# Echo / probe: reject any attempt to supply security context via body.
_FORBIDDEN_BODY_FIELDS = frozenset(
    {"tenant_id", "subject_id", "platform_scope", "session_id", "roles"}
)
# Domain routes: resource ids (e.g. bind credential subject_id) are allowed;
# only ExecutionContext override fields are denied.
_CONTEXT_OVERRIDE_BODY_FIELDS = frozenset({"tenant_id", "platform_scope", "roles"})

_JWT_SETTINGS = JwtSettings.from_env()


def configure_jwt_settings(settings: JwtSettings | None = None) -> JwtSettings:
    """Test helper — replace process JWT settings."""

    global _JWT_SETTINGS
    _JWT_SETTINGS = settings or JwtSettings.from_env()
    return _JWT_SETTINGS


def current_jwt_settings() -> JwtSettings:
    return _JWT_SETTINGS


def derive_tenant_context(
    *,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
    x_eaos_subject_id: Annotated[str | None, Header(alias=_SUBJECT_HEADER)] = None,
    x_eaos_subject_type: Annotated[str | None, Header(alias=_SUBJECT_TYPE_HEADER)] = None,
    x_eaos_tenant_id: Annotated[str | None, Header(alias=_TENANT_HEADER)] = None,
    x_correlation_id: Annotated[str | None, Header(alias=_CORRELATION_HEADER)] = None,
) -> ExecutionContext:
    """Derive tenant data-plane context from Bearer JWT or trusted headers."""

    settings = _JWT_SETTINGS
    bearer = extract_bearer(authorization)
    if bearer is not None:
        claims = verify_token(bearer, _effective_jwt_settings(settings))
        return context_from_tenant_claims(
            claims,
            correlation_header=x_correlation_id,
            eaos_jwt_issuer=settings.issuer,
        )
    if settings.require_jwt:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "GATEWAY_JWT_REQUIRED",
                "message": "Authorization Bearer JWT is required",
            },
        )
    if not settings.allow_dev_headers:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "GATEWAY_AUTH_REQUIRED",
                "message": "Bearer JWT or trusted development headers are required",
            },
        )
    return _tenant_from_headers(
        x_eaos_subject_id=x_eaos_subject_id,
        x_eaos_subject_type=x_eaos_subject_type,
        x_eaos_tenant_id=x_eaos_tenant_id,
        x_correlation_id=x_correlation_id,
    )


def derive_platform_context(
    *,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
    x_eaos_subject_id: Annotated[str | None, Header(alias=_SUBJECT_HEADER)] = None,
    x_eaos_subject_type: Annotated[str | None, Header(alias=_SUBJECT_TYPE_HEADER)] = None,
    x_correlation_id: Annotated[str | None, Header(alias=_CORRELATION_HEADER)] = None,
) -> ExecutionContext:
    """Derive platform control-plane context for /v1/platform/* routes only."""

    settings = _JWT_SETTINGS
    bearer = extract_bearer(authorization)
    if bearer is not None:
        claims = verify_token(bearer, _effective_jwt_settings(settings))
        return context_from_platform_claims(claims, correlation_header=x_correlation_id)
    if settings.require_jwt:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "GATEWAY_JWT_REQUIRED",
                "message": "Authorization Bearer JWT is required",
            },
        )
    if not settings.allow_dev_headers:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "GATEWAY_AUTH_REQUIRED",
                "message": "Bearer JWT or trusted development headers are required",
            },
        )
    return _platform_from_headers(
        x_eaos_subject_id=x_eaos_subject_id,
        x_eaos_subject_type=x_eaos_subject_type,
        x_correlation_id=x_correlation_id,
    )


def reject_body_elevation(body: Mapping[str, Any] | None) -> None:
    """Strict probe helper — used by /v1/context/echo."""

    _reject_fields(body, _FORBIDDEN_BODY_FIELDS)


def reject_context_override(body: Mapping[str, Any] | None) -> None:
    """Domain routes — forbid overriding derived ExecutionContext only."""

    _reject_fields(body, _CONTEXT_OVERRIDE_BODY_FIELDS)


def _tenant_from_headers(
    *,
    x_eaos_subject_id: str | None,
    x_eaos_subject_type: str | None,
    x_eaos_tenant_id: str | None,
    x_correlation_id: str | None,
) -> ExecutionContext:
    if not x_eaos_subject_id or not x_eaos_subject_id.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "CTX_MISSING_SUBJECT",
                "message": "X-EAOS-Subject-Id is required",
            },
        )
    if not x_eaos_tenant_id or not x_eaos_tenant_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "CTX_MISSING_TENANT",
                "message": "X-EAOS-Tenant-Id is required",
            },
        )
    if not x_correlation_id or not x_correlation_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "CTX_MISSING_CORRELATION",
                "message": "X-Correlation-Id is required",
            },
        )
    try:
        subject_id = UUID(x_eaos_subject_id.strip())
        tenant_id = UUID(x_eaos_tenant_id.strip())
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "CTX_INVALID",
                "message": "subject_id and tenant_id must be UUIDs",
            },
        ) from exc
    try:
        subject_type = SubjectType(
            (x_eaos_subject_type or SubjectType.HUMAN.value).strip().casefold()
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "CTX_INVALID",
                "message": "X-EAOS-Subject-Type is invalid",
            },
        ) from exc

    return ExecutionContext(
        subject_id=subject_id,
        subject_type=subject_type,
        tenant_id=tenant_id,
        platform_scope=False,
        correlation_id=x_correlation_id.strip(),
        request_time=ExecutionContext.utc_now(),
    )


def _platform_from_headers(
    *,
    x_eaos_subject_id: str | None,
    x_eaos_subject_type: str | None,
    x_correlation_id: str | None,
) -> ExecutionContext:
    if not x_eaos_subject_id or not x_eaos_subject_id.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "CTX_MISSING_SUBJECT",
                "message": "X-EAOS-Subject-Id is required",
            },
        )
    if not x_correlation_id or not x_correlation_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "CTX_MISSING_CORRELATION",
                "message": "X-Correlation-Id is required",
            },
        )
    try:
        subject_id = UUID(x_eaos_subject_id.strip())
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "CTX_INVALID",
                "message": "subject_id must be a UUID",
            },
        ) from exc
    try:
        subject_type = SubjectType(
            (x_eaos_subject_type or SubjectType.HUMAN.value).strip().casefold()
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "CTX_INVALID",
                "message": "X-EAOS-Subject-Type is invalid",
            },
        ) from exc

    return ExecutionContext(
        subject_id=subject_id,
        subject_type=subject_type,
        tenant_id=None,
        platform_scope=True,
        correlation_id=x_correlation_id.strip(),
        request_time=ExecutionContext.utc_now(),
    )


def _reject_fields(body: Mapping[str, Any] | None, forbidden: frozenset[str]) -> None:
    if not body:
        return
    present = forbidden.intersection(body.keys())
    if present:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "TERMINAL_CONTEXT_ELEVATION_DENIED",
                "message": "security context fields must not be supplied in request body",
                "details": {"fields": sorted(present)},
            },
        )


def serialize_context(ctx: ExecutionContext) -> dict[str, object]:
    return {
        "subject_id": str(ctx.subject_id),
        "subject_type": ctx.subject_type.value,
        "tenant_id": str(ctx.tenant_id) if ctx.tenant_id else None,
        "platform_scope": ctx.platform_scope,
        "correlation_id": ctx.correlation_id,
        "roles": list(ctx.roles),
    }
