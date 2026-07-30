"""Auth / OIDC response DTOs — runtime parity with docs/api/auth.openapi.yaml."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class OidcTokenPayload(_ClosedModel):
    token_type: Literal["Bearer"] = "Bearer"
    access_token: str = Field(min_length=1)
    expires_in: int = Field(ge=1)
    subject_id: UUID
    tenant_id: UUID
    refresh_available: bool | None = None


class OidcTokenEnvelope(_ClosedModel):
    data: OidcTokenPayload


class OidcLogoutPayload(_ClosedModel):
    revoked: bool
    jti: str = Field(min_length=1)
    rp_logout: bool
    end_session_url: str | None = None


class OidcLogoutEnvelope(_ClosedModel):
    data: OidcLogoutPayload


class JwtDenylistPosture(_ClosedModel):
    enabled: bool
    has_json: bool
    has_url: bool
    cache_seconds: int = Field(ge=0)
    configured_entry_count: int | None = None
    load_error: str | None = None
    runtime_revoked_count: int = Field(ge=0)
    url: str | None = None


class JwtStatusData(_ClosedModel):
    writable: Literal[False] = False
    secrets_exposed: Literal[False] = False
    production_auth_fail_closed: Literal[True] = True
    require_jwt: bool
    allow_dev_headers: bool
    multi_issuer: bool
    issuer: str | None = None
    audience: str | None = None
    has_secret: bool
    has_jwks_url: bool
    has_jwks_json: bool
    issuer_count: int = Field(ge=0)
    denylist: JwtDenylistPosture


class JwtStatusEnvelope(_ClosedModel):
    data: JwtStatusData


class OidcLoginProviderPublicItem(_ClosedModel):
    key: str = Field(min_length=1)
    issuer: str = Field(min_length=1)
    has_end_session: bool
    end_session_endpoint: str | None = None


class OidcProvidersPayload(_ClosedModel):
    providers: list[OidcLoginProviderPublicItem]


class OidcProvidersEnvelope(_ClosedModel):
    data: OidcProvidersPayload


class OidcLoginProductPosture(_ClosedModel):
    surface: Literal["foundation_oidc_login_product"] = "foundation_oidc_login_product"
    milestone: Literal["PHX-G147"] = "PHX-G147"
    protocol: Literal["oauth2_authorization_code"] = "oauth2_authorization_code"
    authorization_code_enabled: bool
    live_routes: list[str] = Field(min_length=1)
    fail_closed_when_unconfigured: Literal[True] = True
    fail_closed: bool
    fail_closed_reasons: list[str] = Field(min_length=1)


class WebauthnProductPosture(_ClosedModel):
    surface: Literal["foundation_mfa_webauthn_product"] = "foundation_mfa_webauthn_product"
    milestone: Literal["PHX-G160"] = "PHX-G160"
    webauthn_registration_enabled: bool
    registration_enabled: bool
    webauthn_rp_configured: bool
    webauthn_live_mint_ready: bool
    registration_routes: list[str] = Field(min_length=1)
    ceremony_stub_observability: bool
    registration_default_off: Literal[True] = True
    attestation_crypto_verified: Literal[False] = False
    attestation_mode: Literal["disabled", "challenge_bound"]
    mfa_enrollment_path: Literal["/auth/oidc/mfa-enrollment"] = "/auth/oidc/mfa-enrollment"
    mfa_enrollment_enabled: bool
    mfa_enrollment_url: str | None = None
    live_enroll_path: Literal[
        "webauthn_challenge_bound_mint_g160",
        "idp_redirect_g89_g134",
    ]
    fail_closed_reasons: list[str] = Field(min_length=1)


class OidcStatusData(_ClosedModel):
    enabled: bool
    secrets_exposed: Literal[False] = False
    pkce_s256_required: Literal[True] = True
    issuer: str | None = None
    authorization_endpoint: str | None = None
    token_endpoint: str | None = None
    redirect_uri: str | None = None
    scopes: str
    discovery: bool
    discovery_url: str | None = None
    jwks_uri: str | None = None
    jwks_wire: bool
    discovery_registry_write: bool
    refresh: bool
    refresh_store: str
    refresh_encrypt: str
    refresh_encrypt_key_count: int = Field(ge=0)
    refresh_encrypt_key_provider: str
    refresh_encrypt_kms_backend: str | None = None
    refresh_reencrypt_on_read: bool
    tenant_idp_federation: bool
    required_claims: list[str]
    required_claims_enabled: bool
    required_amr: list[str]
    required_amr_enabled: bool
    required_acr: list[str]
    required_acr_enabled: bool
    role_claim: str | None = None
    role_claim_enabled: bool
    role_map_size: int = Field(ge=0)
    require_mapped_role: bool
    login_providers_enabled: bool
    login_providers: list[OidcLoginProviderPublicItem]
    authorize_stepup_enabled: bool
    authorize_acr_values: str | None = None
    authorize_prompt: str | None = None
    mfa_enrollment_enabled: bool
    mfa_enrollment_url: str | None = None
    oidc_login_product: OidcLoginProductPosture
    webauthn_product: WebauthnProductPosture
    rp_logout: bool
    end_session_endpoint: str | None = None
    has_post_logout_redirect: bool


class OidcStatusEnvelope(_ClosedModel):
    data: OidcStatusData


class IdpJwtIssuerItem(_ClosedModel):
    issuer: str
    jwks_url: str | None = None
    has_jwks_json: bool


class IdpJwtAggregatePosture(_ClosedModel):
    multi_issuer: bool
    issuer: str | None = None
    audience: str | None = None
    has_secret: bool
    has_jwks_url: bool
    has_jwks_json: bool
    require_jwt: bool
    allow_dev_headers: bool
    denylist_enabled: bool
    issuers: list[IdpJwtIssuerItem]


class DiscoveryRegistryWritePosture(_ClosedModel):
    enabled: bool
    action: Literal[
        "skipped",
        "error",
        "unchanged",
        "created",
        "updated",
        "reactivated",
    ]
    issuer: str | None = Field(default=None, min_length=1)
    jwks_url: str | None = Field(default=None, min_length=1)
    id: UUID | None = None
    version: int | None = Field(default=None, ge=0)
    error: str | None = None


class IdpRegistryIssuerStatusItem(_ClosedModel):
    id: UUID
    issuer: str = Field(min_length=1)
    jwks_url: str = Field(min_length=1)
    has_jwks_json: bool
    status: str
    version: int = Field(ge=0)


class IdpRegistryStatusPosture(_ClosedModel):
    writable: bool
    store: Literal["process_memory", "sql", "unavailable"]
    error: str | None = None
    discovery_write: DiscoveryRegistryWritePosture | None = None
    issuers: list[IdpRegistryIssuerStatusItem]


class IdpFederationMatrixSummary(_ClosedModel):
    cell_count: int = Field(ge=0)
    tenant_count: int = Field(ge=0)
    issuer_count: int = Field(ge=0)


class IdpFederationStatusPosture(_ClosedModel):
    enabled: bool
    store: Literal["process_memory", "sql", "unavailable"]
    error: str | None = None
    planes: list[str]
    binding_count: int = Field(ge=0)
    active_count: int = Field(ge=0)
    matrix: IdpFederationMatrixSummary


class IdpStatusData(_ClosedModel):
    writable: Literal[False] = False
    config_source: Literal["environment+registry"] = "environment+registry"
    oidc: OidcStatusData
    jwt: IdpJwtAggregatePosture
    registry: IdpRegistryStatusPosture
    federation: IdpFederationStatusPosture


class IdpStatusEnvelope(_ClosedModel):
    data: IdpStatusData
