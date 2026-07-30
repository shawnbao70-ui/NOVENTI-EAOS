"""WebAuthn ceremony routes (PHX-G151/G154 stubs → PHX-G160 live mint).

Default: options/verify → 503. With EAOS_WEBAUTHN_REGISTRATION_ENABLED +
RP config: challenge-bound live mint into Identity. Single-path
``/auth/webauthn/register`` remains absent.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request

from api.gateway.context import derive_tenant_context, reject_context_override
from api.gateway.deps import IdentityGatewayService, get_identity_service
from api.gateway.schemas.webauthn import (
    WebauthnRegisterOptionsRequest,
    WebauthnRegisterOptionsResponse,
    WebauthnRegisterVerifyRequest,
    WebauthnRegisterVerifyResponse,
)
from api.gateway.webauthn_ceremony import (
    mint_registration_options,
    raise_webauthn_registration_disabled,
    raise_webauthn_rp_config_required,
    verify_and_mint_registration,
    webauthn_registration_enabled,
    webauthn_rp_configured,
)

router = APIRouter(prefix="/v1/auth/webauthn", tags=["Auth"])


def _tenant_ctx(
    *,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
    x_eaos_subject_id: Annotated[str | None, Header(alias="X-EAOS-Subject-Id")] = None,
    x_eaos_subject_type: Annotated[str | None, Header(alias="X-EAOS-Subject-Type")] = None,
    x_eaos_tenant_id: Annotated[str | None, Header(alias="X-EAOS-Tenant-Id")] = None,
    x_correlation_id: Annotated[str | None, Header(alias="X-Correlation-Id")] = None,
):
    return derive_tenant_context(
        authorization=authorization,
        x_eaos_subject_id=x_eaos_subject_id,
        x_eaos_subject_type=x_eaos_subject_type,
        x_eaos_tenant_id=x_eaos_tenant_id,
        x_correlation_id=x_correlation_id,
    )


@router.post("/register/options", response_model=WebauthnRegisterOptionsResponse)
def webauthn_register_options(
    body: WebauthnRegisterOptionsRequest | None = None,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
    x_eaos_subject_id: Annotated[str | None, Header(alias="X-EAOS-Subject-Id")] = None,
    x_eaos_subject_type: Annotated[str | None, Header(alias="X-EAOS-Subject-Type")] = None,
    x_eaos_tenant_id: Annotated[str | None, Header(alias="X-EAOS-Tenant-Id")] = None,
    x_correlation_id: Annotated[str | None, Header(alias="X-Correlation-Id")] = None,
) -> WebauthnRegisterOptionsResponse:
    """Mint PublicKeyCredentialCreationOptions when live mint is enabled."""

    if not webauthn_registration_enabled():
        raise_webauthn_registration_disabled(ceremony_step="register_options")
    if not webauthn_rp_configured():
        raise_webauthn_rp_config_required(ceremony_step="register_options")
    payload = body or WebauthnRegisterOptionsRequest()
    reject_context_override(payload.model_dump(exclude_none=True))
    ctx = _tenant_ctx(
        authorization=authorization,
        x_eaos_subject_id=x_eaos_subject_id,
        x_eaos_subject_type=x_eaos_subject_type,
        x_eaos_tenant_id=x_eaos_tenant_id,
        x_correlation_id=x_correlation_id,
    )
    return WebauthnRegisterOptionsResponse.model_validate(
        mint_registration_options(ctx, payload.model_dump(exclude_none=True))
    )


@router.post("/register/verify", response_model=WebauthnRegisterVerifyResponse)
def webauthn_register_verify(
    request: Request,
    body: WebauthnRegisterVerifyRequest | None = None,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
    x_eaos_subject_id: Annotated[str | None, Header(alias="X-EAOS-Subject-Id")] = None,
    x_eaos_subject_type: Annotated[str | None, Header(alias="X-EAOS-Subject-Type")] = None,
    x_eaos_tenant_id: Annotated[str | None, Header(alias="X-EAOS-Tenant-Id")] = None,
    x_correlation_id: Annotated[str | None, Header(alias="X-Correlation-Id")] = None,
    identity: IdentityGatewayService = Depends(get_identity_service),
) -> WebauthnRegisterVerifyResponse:
    """Challenge-bound verify → Identity webauthn credential mint."""

    _ = request
    if not webauthn_registration_enabled():
        raise_webauthn_registration_disabled(ceremony_step="register_verify")
    if not webauthn_rp_configured():
        raise_webauthn_rp_config_required(ceremony_step="register_verify")
    payload = body or WebauthnRegisterVerifyRequest()
    reject_context_override(payload.model_dump(exclude_none=True))
    ctx = _tenant_ctx(
        authorization=authorization,
        x_eaos_subject_id=x_eaos_subject_id,
        x_eaos_subject_type=x_eaos_subject_type,
        x_eaos_tenant_id=x_eaos_tenant_id,
        x_correlation_id=x_correlation_id,
    )
    return WebauthnRegisterVerifyResponse.model_validate(
        verify_and_mint_registration(
            ctx,
            identity,
            payload.model_dump(exclude_none=True),
        )
    )
