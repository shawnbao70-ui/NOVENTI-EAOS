"""WebAuthn request/response DTOs — runtime parity with docs/api/auth.openapi.yaml."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class WebauthnRegisterOptionsRequest(_ClosedModel):
    """Optional user display overrides for live mint (PHX-G240)."""

    user_name: str | None = None
    user_display_name: str | None = None


class WebauthnRegisterVerifyRequest(BaseModel):
    """Register/verify body — residual browser keys allowed (PHX-G240)."""

    model_config = ConfigDict(extra="allow")

    credential: dict[str, Any] | None = None
    id: str | None = None
    rawId: str | None = None
    type: str | None = None
    response: dict[str, Any] | None = None


class WebauthnRpEntity(_ClosedModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)


class WebauthnUserEntity(_ClosedModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    displayName: str = Field(min_length=1)


class WebauthnPubKeyCredParam(_ClosedModel):
    type: Literal["public-key"] = "public-key"
    alg: int


class WebauthnAuthenticatorSelection(_ClosedModel):
    residentKey: Literal["preferred"] = "preferred"
    userVerification: Literal["preferred"] = "preferred"


class PublicKeyCredentialCreationOptions(_ClosedModel):
    rp: WebauthnRpEntity
    user: WebauthnUserEntity
    challenge: str = Field(min_length=1)
    pubKeyCredParams: list[WebauthnPubKeyCredParam] = Field(min_length=1)
    timeout: Literal[60000] = 60000
    attestation: Literal["none"] = "none"
    authenticatorSelection: WebauthnAuthenticatorSelection


class WebauthnRegisterOptionsResponse(_ClosedModel):
    ceremony_step: Literal["register_options"] = "register_options"
    registration_minted: Literal[False] = False
    attestation_verified: Literal[False] = False
    attestation_crypto_verified: Literal[False] = False
    attestation_mode: Literal["challenge_bound"] = "challenge_bound"
    milestone: str | None = None
    publicKey: PublicKeyCredentialCreationOptions


class WebauthnRegisterVerifyResponse(_ClosedModel):
    ceremony_step: Literal["register_verify"] = "register_verify"
    registration_minted: Literal[True] = True
    attestation_verified: Literal[True] = True
    attestation_crypto_verified: Literal[False] = False
    attestation_mode: Literal["challenge_bound"] = "challenge_bound"
    credential_id: UUID
    credential_kind: Literal["webauthn"] = "webauthn"
    audit_id: UUID | str | None = None
    next_action: Literal["none"] = "none"
    milestone: str | None = None
