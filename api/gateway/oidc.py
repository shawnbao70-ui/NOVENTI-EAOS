"""OIDC Authorization Code + PKCE helpers (PHX-G40/G47/G48/G60/G61)."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Protocol
from uuid import UUID, uuid5, NAMESPACE_URL

from fastapi import HTTPException, status

from api.gateway.auth_jwt import JwtIssuerBinding, JwtSettings, mint_hs256_token
from api.gateway.oidc_refresh_crypto import (
    refresh_encrypt_key_count,
    refresh_encrypt_kms_backend_label,
    refresh_key_provider,
    refresh_reencrypt_on_read_enabled,
)
from api.gateway.oidc_amr_acr import (
    assert_oidc_amr_acr,
    oidc_required_acr,
    oidc_required_acr_enabled,
    oidc_required_amr,
    oidc_required_amr_enabled,
)
from api.gateway.oidc_authorize_stepup import (
    oidc_authorize_acr_values,
    oidc_authorize_prompt,
    oidc_authorize_stepup_enabled,
    oidc_authorize_stepup_params,
)
from api.gateway.oidc_mfa_enrollment import (
    oidc_mfa_enrollment_enabled,
    oidc_mfa_enrollment_url,
)
from api.gateway.oidc_login_product import oidc_login_product_posture
from api.gateway.webauthn_product import webauthn_product_posture
from api.gateway.oidc_claim_role import (
    assert_oidc_mapped_roles,
    map_oidc_roles,
    oidc_require_mapped_role,
    oidc_role_claim,
    oidc_role_claim_enabled,
    oidc_role_map,
)
from api.gateway.oidc_login_providers import (
    get_oidc_login_provider,
    oidc_login_providers_enabled,
    oidc_login_providers_public,
)
from api.gateway.oidc_required_claims import (
    assert_oidc_required_claims,
    oidc_required_claims,
    oidc_required_claims_enabled,
)
from api.gateway.oidc_refresh_store import (
    OidcSessionBinding,
    clear_oidc_refresh_store,
    get_oidc_session,
    pop_oidc_session,
    put_oidc_session,
    refresh_encrypt_label,
    refresh_store_label,
)
from api.gateway.tenant_idp_federation import (
    assert_tenant_idp_binding,
    tenant_idp_federation_enabled,
)

_DISCOVERY_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
_DISCOVERY_CACHE_SECONDS = 300


def _optional(name: str) -> str | None:
    value = os.environ.get(name, "").strip()
    return value or None


def _env_flag(name: str, *, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    return str(raw).strip().casefold() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class OidcSettings:
    issuer: str | None
    client_id: str | None
    client_secret: str | None
    redirect_uri: str | None
    authorization_endpoint: str | None
    token_endpoint: str | None
    scopes: str
    default_tenant_id: str | None
    enabled: bool
    discovery: bool = False
    discovery_url: str | None = None
    jwks_uri: str | None = None
    jwks_wire: bool = False
    discovery_registry_write: bool = False
    refresh: bool = False
    rp_logout: bool = False
    end_session_endpoint: str | None = None
    post_logout_redirect_uri: str | None = None

    @classmethod
    def from_env(cls) -> OidcSettings:
        issuer = _optional("EAOS_OIDC_ISSUER")
        client_id = _optional("EAOS_OIDC_CLIENT_ID")
        redirect_uri = _optional("EAOS_OIDC_REDIRECT_URI")
        authorization_endpoint = _optional("EAOS_OIDC_AUTHORIZATION_ENDPOINT")
        token_endpoint = _optional("EAOS_OIDC_TOKEN_ENDPOINT")
        discovery = _env_flag("EAOS_OIDC_DISCOVERY", default=False)
        discovery_url = _optional("EAOS_OIDC_DISCOVERY_URL")
        jwks_wire = _env_flag("EAOS_OIDC_JWKS_WIRE", default=False)
        discovery_registry_write = _env_flag(
            "EAOS_OIDC_DISCOVERY_REGISTRY_WRITE",
            default=False,
        )
        refresh = _env_flag("EAOS_OIDC_REFRESH", default=False)
        rp_logout = _env_flag("EAOS_OIDC_RP_LOGOUT", default=False)
        end_session_endpoint = _optional("EAOS_OIDC_END_SESSION_ENDPOINT")
        post_logout_redirect_uri = _optional("EAOS_OIDC_POST_LOGOUT_REDIRECT_URI")
        if discovery and issuer and not discovery_url:
            discovery_url = issuer.rstrip("/") + "/.well-known/openid-configuration"
        if not discovery:
            if issuer and not authorization_endpoint:
                authorization_endpoint = issuer.rstrip("/") + "/authorize"
            if issuer and not token_endpoint:
                token_endpoint = issuer.rstrip("/") + "/token"
        endpoints_ready = bool(authorization_endpoint and token_endpoint)
        enabled = bool(
            issuer
            and client_id
            and redirect_uri
            and (endpoints_ready or discovery)
        )
        return cls(
            issuer=issuer,
            client_id=client_id,
            client_secret=_optional("EAOS_OIDC_CLIENT_SECRET"),
            redirect_uri=redirect_uri,
            authorization_endpoint=authorization_endpoint,
            token_endpoint=token_endpoint,
            scopes=_optional("EAOS_OIDC_SCOPES") or "openid profile",
            default_tenant_id=_optional("EAOS_OIDC_DEFAULT_TENANT_ID"),
            enabled=enabled,
            discovery=discovery,
            discovery_url=discovery_url,
            jwks_wire=jwks_wire,
            discovery_registry_write=discovery_registry_write,
            refresh=refresh,
            rp_logout=rp_logout,
            end_session_endpoint=end_session_endpoint,
            post_logout_redirect_uri=post_logout_redirect_uri,
        )


@dataclass(slots=True)
class OidcLoginState:
    code_verifier: str
    created_at: float
    nonce: str
    provider_key: str | None = None


class OidcTokenClient(Protocol):
    def exchange_code(
        self,
        *,
        token_endpoint: str,
        client_id: str,
        client_secret: str | None,
        code: str,
        redirect_uri: str,
        code_verifier: str,
    ) -> dict[str, Any]: ...

    def refresh(
        self,
        *,
        token_endpoint: str,
        client_id: str,
        client_secret: str | None,
        refresh_token: str,
    ) -> dict[str, Any]: ...


class OidcDiscoveryClient(Protocol):
    def fetch(self, url: str) -> dict[str, Any]: ...


class UrllibOidcDiscoveryClient:
    def fetch(self, url: str) -> dict[str, Any]:
        _require_https_or_loopback(url, purpose="OIDC discovery")
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "NOVENTI-EAOS-Gateway/0.2",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310
                raw = response.read()
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "GATEWAY_OIDC_DISCOVERY_FAILED",
                    "message": "OIDC discovery fetch failed",
                },
            ) from exc
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "GATEWAY_OIDC_DISCOVERY_FAILED",
                    "message": "OIDC discovery returned invalid JSON",
                },
            ) from exc
        if not isinstance(payload, dict):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "GATEWAY_OIDC_DISCOVERY_FAILED",
                    "message": "OIDC discovery document must be an object",
                },
            )
        return payload


class UrllibOidcTokenClient:
    def exchange_code(
        self,
        *,
        token_endpoint: str,
        client_id: str,
        client_secret: str | None,
        code: str,
        redirect_uri: str,
        code_verifier: str,
    ) -> dict[str, Any]:
        _require_https_or_loopback(token_endpoint, purpose="OIDC token_endpoint")
        form = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "code_verifier": code_verifier,
        }
        if client_secret:
            form["client_secret"] = client_secret
        body = urllib.parse.urlencode(form).encode("utf-8")
        request = urllib.request.Request(
            token_endpoint,
            data=body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "User-Agent": "NOVENTI-EAOS-Gateway/0.2",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310
                raw = response.read()
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "code": "GATEWAY_OIDC_TOKEN_EXCHANGE_FAILED",
                    "message": "OIDC token exchange failed",
                },
            ) from exc
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "code": "GATEWAY_OIDC_TOKEN_EXCHANGE_FAILED",
                    "message": "OIDC token endpoint returned invalid JSON",
                },
            ) from exc
        if not isinstance(payload, dict):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "code": "GATEWAY_OIDC_TOKEN_EXCHANGE_FAILED",
                    "message": "OIDC token endpoint returned non-object JSON",
                },
            )
        return payload

    def refresh(
        self,
        *,
        token_endpoint: str,
        client_id: str,
        client_secret: str | None,
        refresh_token: str,
    ) -> dict[str, Any]:
        _require_https_or_loopback(token_endpoint, purpose="OIDC token_endpoint")
        form = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
        }
        if client_secret:
            form["client_secret"] = client_secret
        body = urllib.parse.urlencode(form).encode("utf-8")
        request = urllib.request.Request(
            token_endpoint,
            data=body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "User-Agent": "NOVENTI-EAOS-Gateway/0.2",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310
                raw = response.read()
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "code": "GATEWAY_OIDC_REFRESH_FAILED",
                    "message": "OIDC refresh_token grant failed",
                },
            ) from exc
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "code": "GATEWAY_OIDC_REFRESH_FAILED",
                    "message": "OIDC token endpoint returned invalid JSON on refresh",
                },
            ) from exc
        if not isinstance(payload, dict):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "code": "GATEWAY_OIDC_REFRESH_FAILED",
                    "message": "OIDC token endpoint returned non-object JSON on refresh",
                },
            )
        return payload


_OIDC_SETTINGS = OidcSettings.from_env()
_OIDC_STATES: dict[str, OidcLoginState] = {}
_TOKEN_CLIENT: OidcTokenClient = UrllibOidcTokenClient()
_DISCOVERY_CLIENT: OidcDiscoveryClient = UrllibOidcDiscoveryClient()
_STATE_TTL_SECONDS = 600
_LAST_DISCOVERY_REGISTRY_WRITE: dict[str, Any] | None = None
_SYNCED_DISCOVERY_KEY: tuple[str, str] | None = None


def configure_oidc(
    settings: OidcSettings | None = None,
    *,
    token_client: OidcTokenClient | None = None,
    discovery_client: OidcDiscoveryClient | None = None,
) -> OidcSettings:
    """Test helper — replace OIDC settings / clients."""

    global _OIDC_SETTINGS, _TOKEN_CLIENT, _DISCOVERY_CLIENT
    global _LAST_DISCOVERY_REGISTRY_WRITE, _SYNCED_DISCOVERY_KEY
    _OIDC_SETTINGS = settings or OidcSettings.from_env()
    _LAST_DISCOVERY_REGISTRY_WRITE = None
    _SYNCED_DISCOVERY_KEY = None
    if token_client is not None:
        _TOKEN_CLIENT = token_client
    if discovery_client is not None:
        _DISCOVERY_CLIENT = discovery_client
    return _OIDC_SETTINGS


def clear_oidc_states() -> None:
    _OIDC_STATES.clear()
    clear_oidc_refresh_store()


def clear_oidc_discovery_cache() -> None:
    _DISCOVERY_CACHE.clear()


def clear_discovery_registry_write_state() -> None:
    global _LAST_DISCOVERY_REGISTRY_WRITE, _SYNCED_DISCOVERY_KEY
    _LAST_DISCOVERY_REGISTRY_WRITE = None
    _SYNCED_DISCOVERY_KEY = None


def discovery_registry_write_status() -> dict[str, Any] | None:
    return _LAST_DISCOVERY_REGISTRY_WRITE


def oidc_status() -> dict[str, Any]:
    settings = _OIDC_SETTINGS
    resolved = settings
    if settings.enabled and settings.discovery:
        try:
            resolved = resolve_oidc_endpoints(settings)
        except HTTPException:
            resolved = settings
    return {
        "enabled": settings.enabled,
        "secrets_exposed": False,
        "pkce_s256_required": True,
        "issuer": settings.issuer,
        "authorization_endpoint": resolved.authorization_endpoint,
        "token_endpoint": resolved.token_endpoint,
        "redirect_uri": settings.redirect_uri,
        "scopes": settings.scopes,
        "discovery": settings.discovery,
        "discovery_url": settings.discovery_url,
        "jwks_uri": resolved.jwks_uri,
        "jwks_wire": settings.jwks_wire,
        "discovery_registry_write": settings.discovery_registry_write,
        "refresh": settings.refresh,
        "refresh_store": refresh_store_label(),
        "refresh_encrypt": refresh_encrypt_label(),
        "refresh_encrypt_key_count": refresh_encrypt_key_count(),
        "refresh_encrypt_key_provider": refresh_key_provider(),
        "refresh_encrypt_kms_backend": refresh_encrypt_kms_backend_label(),
        "refresh_reencrypt_on_read": refresh_reencrypt_on_read_enabled(),
        "tenant_idp_federation": tenant_idp_federation_enabled(),
        "required_claims": oidc_required_claims(),
        "required_claims_enabled": oidc_required_claims_enabled(),
        "required_amr": oidc_required_amr(),
        "required_amr_enabled": oidc_required_amr_enabled(),
        "required_acr": oidc_required_acr(),
        "required_acr_enabled": oidc_required_acr_enabled(),
        "role_claim": oidc_role_claim(),
        "role_claim_enabled": oidc_role_claim_enabled(),
        "role_map_size": len(oidc_role_map()),
        "require_mapped_role": oidc_require_mapped_role(),
        "login_providers_enabled": oidc_login_providers_enabled(),
        "login_providers": oidc_login_providers_public(),
        "authorize_stepup_enabled": oidc_authorize_stepup_enabled(),
        "authorize_acr_values": oidc_authorize_acr_values(),
        "authorize_prompt": oidc_authorize_prompt(),
        "mfa_enrollment_enabled": oidc_mfa_enrollment_enabled(),
        "mfa_enrollment_url": oidc_mfa_enrollment_url(),
        "oidc_login_product": oidc_login_product_posture(
            authorization_code_enabled=settings.enabled,
        ),
        "webauthn_product": webauthn_product_posture(),
        "rp_logout": settings.rp_logout,
        "end_session_endpoint": resolved.end_session_endpoint,
        "has_post_logout_redirect": bool(settings.post_logout_redirect_uri),
    }


def begin_oidc_login(*, provider: str | None = None) -> str:
    settings = resolve_login_oidc_settings(provider)
    state = secrets.token_urlsafe(24)
    verifier = secrets.token_urlsafe(48)
    nonce = secrets.token_urlsafe(24)
    provider_key = (provider or "").strip() or None
    _purge_expired_states()
    _OIDC_STATES[state] = OidcLoginState(
        code_verifier=verifier,
        created_at=time.time(),
        nonce=nonce,
        provider_key=provider_key,
    )
    challenge = _pkce_challenge(verifier)
    params: dict[str, str] = {
        "response_type": "code",
        "client_id": settings.client_id or "",
        "redirect_uri": settings.redirect_uri or "",
        "scope": settings.scopes,
        "state": state,
        "nonce": nonce,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    params.update(oidc_authorize_stepup_params())
    query = urllib.parse.urlencode(params)
    assert settings.authorization_endpoint is not None
    return f"{settings.authorization_endpoint}?{query}"


def complete_oidc_callback(
    *,
    code: str,
    state: str,
    jwt_settings: JwtSettings,
) -> dict[str, Any]:
    if not code.strip() or not state.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "GATEWAY_OIDC_INVALID",
                "message": "code and state are required",
            },
        )
    login_state = _OIDC_STATES.pop(state.strip(), None)
    if login_state is None or time.time() - login_state.created_at > _STATE_TTL_SECONDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "GATEWAY_OIDC_INVALID_STATE",
                "message": "OIDC state is invalid or expired",
            },
        )
    settings = resolve_login_oidc_settings(login_state.provider_key)
    if not jwt_settings.secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_JWT_UNCONFIGURED",
                "message": "EAOS_JWT_SECRET is required to mint EAOS tokens after OIDC login",
            },
        )
    assert settings.token_endpoint is not None
    assert settings.client_id is not None
    assert settings.redirect_uri is not None
    token_payload = _TOKEN_CLIENT.exchange_code(
        token_endpoint=settings.token_endpoint,
        client_id=settings.client_id,
        client_secret=settings.client_secret,
        code=code.strip(),
        redirect_uri=settings.redirect_uri,
        code_verifier=login_state.code_verifier,
    )
    id_token = token_payload.get("id_token")
    if not isinstance(id_token, str) or not id_token.strip():
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "code": "GATEWAY_OIDC_TOKEN_EXCHANGE_FAILED",
                "message": "OIDC token response missing id_token",
            },
        )
    id_claims = _unsafe_decode_jwt_payload(id_token)
    eaos_claims = map_oidc_claims_to_eaos(
        id_claims,
        settings=settings,
        nonce=login_state.nonce,
    )
    _attach_login_provider_claim(eaos_claims, login_state.provider_key)
    if jwt_settings.issuer:
        eaos_claims["iss"] = jwt_settings.issuer
    if jwt_settings.audience:
        eaos_claims["aud"] = jwt_settings.audience
    access_token = mint_hs256_token(eaos_claims, secret=jwt_settings.secret)
    jti = str(eaos_claims.get("jti") or "").strip()
    if jti and (settings.refresh or settings.rp_logout):
        refresh_token = token_payload.get("refresh_token")
        refresh_value = (
            refresh_token.strip()
            if settings.refresh
            and isinstance(refresh_token, str)
            and refresh_token.strip()
            else None
        )
        put_oidc_session(
            jti,
            OidcSessionBinding(
                refresh_token=refresh_value,
                id_token=id_token.strip(),
                created_at=time.time(),
            ),
        )
    bound = get_oidc_session(jti) if jti else None
    return {
        "token_type": "Bearer",
        "access_token": access_token,
        "expires_in": 3600,
        "subject_id": eaos_claims["sub"],
        "tenant_id": eaos_claims["eaos_tenant_id"],
        "refresh_available": bool(
            settings.refresh and bound is not None and bound.refresh_token
        ),
    }


def map_oidc_claims_to_eaos(
    id_claims: dict[str, Any],
    *,
    settings: OidcSettings,
    nonce: str | None = None,
) -> dict[str, Any]:
    if nonce is not None and "nonce" in id_claims and id_claims.get("nonce") != nonce:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "GATEWAY_OIDC_INVALID",
                "message": "OIDC nonce mismatch",
            },
        )
    assert_oidc_required_claims(id_claims)
    assert_oidc_amr_acr(id_claims)
    mapped_roles = map_oidc_roles(id_claims)
    assert_oidc_mapped_roles(mapped_roles)
    raw_sub = id_claims.get("sub")
    if raw_sub is None or str(raw_sub).strip() == "":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "GATEWAY_OIDC_INVALID",
                "message": "OIDC id_token missing sub",
            },
        )
    subject_id = _subject_uuid(str(raw_sub), issuer=settings.issuer or "eaos-oidc")
    tenant_raw = id_claims.get("eaos_tenant_id") or settings.default_tenant_id
    if tenant_raw is None or str(tenant_raw).strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "GATEWAY_OIDC_INVALID",
                "message": "eaos_tenant_id claim or EAOS_OIDC_DEFAULT_TENANT_ID is required",
            },
        )
    try:
        tenant_id = str(UUID(str(tenant_raw).strip()))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "GATEWAY_OIDC_INVALID",
                "message": "tenant id must be a UUID",
            },
        ) from exc
    assert_tenant_idp_binding(tenant_id=tenant_id, issuer=settings.issuer)
    subject_type = str(id_claims.get("eaos_subject_type") or "human").strip().casefold()
    now = int(time.time())
    claims: dict[str, Any] = {
        "sub": subject_id,
        "eaos_tenant_id": tenant_id,
        "eaos_subject_type": subject_type,
        "exp": now + 3600,
        "iat": now,
        "jti": secrets.token_urlsafe(12),
    }
    if mapped_roles:
        claims["eaos_roles"] = mapped_roles
    if settings.issuer:
        # EAOS token issuer remains JWT settings; keep oidc provenance in claim
        claims["eaos_oidc_issuer"] = settings.issuer
    return claims


def _require_configured() -> OidcSettings:
    settings = _OIDC_SETTINGS
    if not settings.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_OIDC_UNCONFIGURED",
                "message": "OIDC is not configured (EAOS_OIDC_* env)",
            },
        )
    if settings.discovery:
        return resolve_oidc_endpoints(settings)
    if not settings.authorization_endpoint or not settings.token_endpoint:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_OIDC_UNCONFIGURED",
                "message": "OIDC authorization_endpoint and token_endpoint are required",
            },
        )
    return settings


def resolve_login_oidc_settings(provider: str | None) -> OidcSettings:
    """Primary OIDC settings, or overlay from ``EAOS_OIDC_LOGIN_PROVIDERS`` (PHX-G84–G86)."""

    primary = _require_configured()
    key = (provider or "").strip()
    if not key:
        return primary
    entry = get_oidc_login_provider(key)
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "GATEWAY_OIDC_UNKNOWN_PROVIDER",
                "message": f"OIDC login provider '{key}' is not configured",
            },
        )
    issuer = entry.issuer
    authorize = entry.authorization_endpoint or f"{issuer}/authorize"
    token = entry.token_endpoint or f"{issuer}/token"
    end_session = entry.end_session_endpoint or primary.end_session_endpoint
    return OidcSettings(
        issuer=issuer,
        client_id=entry.client_id,
        client_secret=entry.client_secret,
        redirect_uri=primary.redirect_uri,
        authorization_endpoint=authorize,
        token_endpoint=token,
        scopes=primary.scopes,
        default_tenant_id=primary.default_tenant_id,
        enabled=True,
        discovery=False,
        discovery_url=None,
        jwks_uri=None,
        jwks_wire=False,
        discovery_registry_write=False,
        refresh=primary.refresh,
        rp_logout=primary.rp_logout,
        end_session_endpoint=end_session,
        post_logout_redirect_uri=primary.post_logout_redirect_uri,
    )


def _login_provider_from_claims(claims: dict[str, Any]) -> str | None:
    raw = claims.get("eaos_oidc_login_provider")
    if raw is None:
        return None
    text = str(raw).strip()
    return text or None


def _attach_login_provider_claim(
    eaos_claims: dict[str, Any],
    provider_key: str | None,
) -> None:
    key = (provider_key or "").strip()
    if key:
        eaos_claims["eaos_oidc_login_provider"] = key
    else:
        eaos_claims.pop("eaos_oidc_login_provider", None)


def resolve_oidc_endpoints(settings: OidcSettings) -> OidcSettings:
    """Fill missing authorize/token endpoints from OpenID Provider Metadata."""

    if not settings.discovery:
        return settings
    if not settings.discovery_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_OIDC_DISCOVERY_FAILED",
                "message": "OIDC discovery URL is not configured",
            },
        )
    document = _load_discovery_document(settings.discovery_url)
    discovered_issuer = str(document.get("issuer") or "").strip()
    if settings.issuer and discovered_issuer and discovered_issuer != settings.issuer:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_OIDC_DISCOVERY_FAILED",
                "message": "OIDC discovery issuer does not match EAOS_OIDC_ISSUER",
            },
        )
    authorization_endpoint = settings.authorization_endpoint or str(
        document.get("authorization_endpoint") or ""
    ).strip() or None
    token_endpoint = settings.token_endpoint or str(
        document.get("token_endpoint") or ""
    ).strip() or None
    jwks_uri = settings.jwks_uri or str(document.get("jwks_uri") or "").strip() or None
    end_session_endpoint = settings.end_session_endpoint or str(
        document.get("end_session_endpoint") or ""
    ).strip() or None
    if not authorization_endpoint or not token_endpoint:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_OIDC_DISCOVERY_FAILED",
                "message": "OIDC discovery missing authorization_endpoint or token_endpoint",
            },
        )
    return OidcSettings(
        issuer=settings.issuer,
        client_id=settings.client_id,
        client_secret=settings.client_secret,
        redirect_uri=settings.redirect_uri,
        authorization_endpoint=authorization_endpoint,
        token_endpoint=token_endpoint,
        scopes=settings.scopes,
        default_tenant_id=settings.default_tenant_id,
        enabled=settings.enabled,
        discovery=settings.discovery,
        discovery_url=settings.discovery_url,
        jwks_uri=jwks_uri,
        jwks_wire=settings.jwks_wire,
        discovery_registry_write=settings.discovery_registry_write,
        refresh=settings.refresh,
        rp_logout=settings.rp_logout,
        end_session_endpoint=end_session_endpoint,
        post_logout_redirect_uri=settings.post_logout_redirect_uri,
    )


def refresh_eaos_token(
    *,
    claims: dict[str, Any],
    jwt_settings: JwtSettings,
) -> dict[str, Any]:
    """Exchange stored IdP refresh_token for a new EAOS Bearer (PHX-G61/G85)."""

    provider_key = _login_provider_from_claims(claims)
    settings = resolve_login_oidc_settings(provider_key)
    if not settings.refresh:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_OIDC_REFRESH_DISABLED",
                "message": "EAOS_OIDC_REFRESH is not enabled",
            },
        )
    if not jwt_settings.secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_JWT_UNCONFIGURED",
                "message": "EAOS_JWT_SECRET is required to mint refreshed EAOS tokens",
            },
        )
    jti = str(claims.get("jti") or "").strip()
    if not jti:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "GATEWAY_OIDC_REFRESH_FAILED",
                "message": "EAOS token missing jti for refresh binding",
            },
        )
    try:
        binding = get_oidc_session(jti)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_OIDC_REFRESH_STORE_UNAVAILABLE",
                "message": str(exc),
            },
        ) from exc
    if binding is None or not binding.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "GATEWAY_OIDC_REFRESH_FAILED",
                "message": "no refresh session is bound to this EAOS token",
            },
        )
    assert settings.token_endpoint is not None
    assert settings.client_id is not None
    token_payload = _TOKEN_CLIENT.refresh(
        token_endpoint=settings.token_endpoint,
        client_id=settings.client_id,
        client_secret=settings.client_secret,
        refresh_token=binding.refresh_token,
    )
    id_token = token_payload.get("id_token")
    if isinstance(id_token, str) and id_token.strip():
        id_claims = _unsafe_decode_jwt_payload(id_token)
        eaos_claims = map_oidc_claims_to_eaos(id_claims, settings=settings, nonce=None)
    else:
        # Some IdPs omit id_token on refresh; re-mint from existing EAOS claims
        assert_tenant_idp_binding(
            tenant_id=claims["eaos_tenant_id"],
            issuer=settings.issuer,
        )
        now = int(time.time())
        eaos_claims = {
            "sub": claims["sub"],
            "eaos_tenant_id": claims["eaos_tenant_id"],
            "eaos_subject_type": claims.get("eaos_subject_type") or "human",
            "exp": now + 3600,
            "iat": now,
            "jti": secrets.token_urlsafe(12),
        }
        if settings.issuer:
            eaos_claims["eaos_oidc_issuer"] = settings.issuer
        roles = claims.get("eaos_roles")
        if isinstance(roles, list) and roles:
            eaos_claims["eaos_roles"] = roles
        id_token = binding.id_token
    _attach_login_provider_claim(eaos_claims, provider_key)
    if jwt_settings.issuer:
        eaos_claims["iss"] = jwt_settings.issuer
    if jwt_settings.audience:
        eaos_claims["aud"] = jwt_settings.audience
    access_token = mint_hs256_token(eaos_claims, secret=jwt_settings.secret)
    new_jti = str(eaos_claims.get("jti") or "").strip()
    new_refresh = token_payload.get("refresh_token")
    refresh_value = (
        new_refresh.strip()
        if isinstance(new_refresh, str) and new_refresh.strip()
        else binding.refresh_token
    )
    from api.gateway.auth_jwt import revoke_runtime_jti

    revoke_runtime_jti(jti, iss=str(claims.get("iss") or "").strip() or None)
    pop_oidc_session(jti)
    if new_jti and refresh_value:
        put_oidc_session(
            new_jti,
            OidcSessionBinding(
                refresh_token=refresh_value,
                id_token=(
                    id_token.strip()
                    if isinstance(id_token, str) and id_token.strip()
                    else binding.id_token
                ),
                created_at=time.time(),
            ),
        )
    from api.gateway.schemas.auth import OidcTokenPayload

    return OidcTokenPayload.model_validate(
        {
            "token_type": "Bearer",
            "access_token": access_token,
            "expires_in": 3600,
            "subject_id": eaos_claims["sub"],
            "tenant_id": eaos_claims["eaos_tenant_id"],
            "refresh_available": bool(
                new_jti and get_oidc_session(new_jti) is not None
            ),
        }
    ).model_dump(mode="json")


def logout_eaos_session(
    *,
    claims: dict[str, Any],
) -> dict[str, Any]:
    """Locally revoke EAOS jti; optionally return RP-Logout URL (PHX-G61/G85)."""

    settings = resolve_login_oidc_settings(_login_provider_from_claims(claims))
    jti = str(claims.get("jti") or "").strip()
    if not jti:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "GATEWAY_OIDC_LOGOUT_FAILED",
                "message": "EAOS token missing jti for logout",
            },
        )
    from api.gateway.auth_jwt import revoke_runtime_jti

    revoke_runtime_jti(jti, iss=str(claims.get("iss") or "").strip() or None)
    try:
        binding = pop_oidc_session(jti)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_OIDC_REFRESH_STORE_UNAVAILABLE",
                "message": str(exc),
            },
        ) from exc
    from api.gateway.schemas.auth import OidcLogoutPayload

    result: dict[str, Any] = {
        "revoked": True,
        "jti": jti,
        "rp_logout": False,
        "end_session_url": None,
    }
    if not settings.rp_logout:
        return OidcLogoutPayload.model_validate(result).model_dump(mode="json")
    resolved = settings
    if settings.discovery:
        try:
            resolved = resolve_oidc_endpoints(settings)
        except HTTPException:
            resolved = settings
    endpoint = resolved.end_session_endpoint
    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_OIDC_LOGOUT_FAILED",
                "message": "EAOS_OIDC_RP_LOGOUT requires end_session_endpoint",
            },
        )
    query: dict[str, str] = {}
    if binding and binding.id_token:
        query["id_token_hint"] = binding.id_token
    if settings.post_logout_redirect_uri:
        query["post_logout_redirect_uri"] = settings.post_logout_redirect_uri
    if settings.client_id:
        query["client_id"] = settings.client_id
    end_session_url = endpoint
    if query:
        end_session_url = f"{endpoint}?{urllib.parse.urlencode(query)}"
    result["rp_logout"] = True
    result["end_session_url"] = end_session_url
    return OidcLogoutPayload.model_validate(result).model_dump(mode="json")


def maybe_write_discovery_to_registry(*, raise_on_error: bool = True) -> dict[str, Any]:
    """Upsert Discovery jwks_uri into IdP registry when opt-in flag is on (PHX-G60)."""

    global _LAST_DISCOVERY_REGISTRY_WRITE, _SYNCED_DISCOVERY_KEY
    oidc = _OIDC_SETTINGS
    if not oidc.discovery_registry_write:
        result = {"enabled": False, "action": "skipped"}
        _LAST_DISCOVERY_REGISTRY_WRITE = result
        return result
    if not oidc.enabled or not oidc.discovery:
        detail = {
            "code": "GATEWAY_OIDC_DISCOVERY_WRITE_FAILED",
            "message": "EAOS_OIDC_DISCOVERY_REGISTRY_WRITE requires OIDC Discovery to be enabled",
        }
        if raise_on_error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=detail,
            )
        result = {"enabled": True, "action": "error", "error": detail["message"]}
        _LAST_DISCOVERY_REGISTRY_WRITE = result
        return result

    try:
        resolved = resolve_oidc_endpoints(oidc)
        if not resolved.issuer or not resolved.jwks_uri:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "GATEWAY_OIDC_DISCOVERY_WRITE_FAILED",
                    "message": "OIDC discovery missing issuer or jwks_uri for registry write",
                },
            )
        _require_https_or_loopback(resolved.jwks_uri, purpose="OIDC jwks_uri")
        key = (resolved.issuer, resolved.jwks_uri)
        if _SYNCED_DISCOVERY_KEY == key:
            result = {
                "enabled": True,
                "action": "unchanged",
                "issuer": resolved.issuer,
                "jwks_url": resolved.jwks_uri,
            }
            _LAST_DISCOVERY_REGISTRY_WRITE = result
            return result

        from api.gateway.idp_registry import upsert_idp_issuer

        record, action = upsert_idp_issuer(
            issuer=resolved.issuer,
            jwks_url=resolved.jwks_uri,
            jwks_json=None,
        )
        _SYNCED_DISCOVERY_KEY = key
        result = {
            "enabled": True,
            "action": action,
            "issuer": record.issuer,
            "jwks_url": record.jwks_url,
            "id": str(record.id),
            "version": record.version,
        }
        _LAST_DISCOVERY_REGISTRY_WRITE = result
        return result
    except HTTPException as exc:
        if raise_on_error:
            raise
        message = ""
        if isinstance(exc.detail, dict):
            message = str(exc.detail.get("message") or "")
        else:
            message = str(exc.detail)
        result = {"enabled": True, "action": "error", "error": message}
        _LAST_DISCOVERY_REGISTRY_WRITE = result
        return result


def maybe_wire_discovery_jwks(settings: JwtSettings) -> JwtSettings:
    """Inject Discovery jwks_uri into JWT allowlist when EAOS_OIDC_JWKS_WIRE is on."""

    oidc = _OIDC_SETTINGS
    if not oidc.jwks_wire:
        return settings
    if settings.issuers or settings.jwks_json or settings.jwks_url:
        return settings
    if not oidc.enabled or not oidc.discovery:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_OIDC_JWKS_WIRE_FAILED",
                "message": "EAOS_OIDC_JWKS_WIRE requires OIDC Discovery to be enabled",
            },
        )
    resolved = resolve_oidc_endpoints(oidc)
    if not resolved.issuer or not resolved.jwks_uri:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_OIDC_JWKS_WIRE_FAILED",
                "message": "OIDC discovery missing issuer or jwks_uri for JWKS wire",
            },
        )
    _require_https_or_loopback(resolved.jwks_uri, purpose="OIDC jwks_uri")
    bindings: list[JwtIssuerBinding] = [
        JwtIssuerBinding(issuer=resolved.issuer, jwks_url=resolved.jwks_uri)
    ]
    if (
        settings.secret
        and settings.issuer
        and settings.issuer != resolved.issuer
    ):
        bindings.append(JwtIssuerBinding(issuer=settings.issuer))
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
        issuers=tuple(bindings),
        denylist_json=settings.denylist_json,
        denylist_url=settings.denylist_url,
        denylist_cache_seconds=settings.denylist_cache_seconds,
    )


def _load_discovery_document(url: str) -> dict[str, Any]:
    now = time.time()
    cached = _DISCOVERY_CACHE.get(url)
    if cached is not None and cached[0] > now:
        return cached[1]
    document = _DISCOVERY_CLIENT.fetch(url)
    _DISCOVERY_CACHE[url] = (now + _DISCOVERY_CACHE_SECONDS, document)
    return document


def _require_https_or_loopback(url: str, *, purpose: str) -> None:
    lowered = url.casefold()
    if lowered.startswith("https://"):
        return
    if lowered.startswith("http://127.0.0.1") or lowered.startswith("http://localhost"):
        return
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "code": "GATEWAY_OIDC_UNCONFIGURED",
            "message": f"{purpose} must use https",
        },
    )


def _purge_expired_states() -> None:
    now = time.time()
    expired = [
        key
        for key, value in _OIDC_STATES.items()
        if now - value.created_at > _STATE_TTL_SECONDS
    ]
    for key in expired:
        _OIDC_STATES.pop(key, None)


def _pkce_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def _unsafe_decode_jwt_payload(token: str) -> dict[str, Any]:
    """Decode JWT payload without signature verify — IdP TLS + code exchange is the trust."""

    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "code": "GATEWAY_OIDC_TOKEN_EXCHANGE_FAILED",
                "message": "id_token is not a JWT",
            },
        )
    padding = "=" * (-len(parts[1]) % 4)
    try:
        raw = base64.urlsafe_b64decode(parts[1] + padding)
        payload = json.loads(raw.decode("utf-8"))
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "code": "GATEWAY_OIDC_TOKEN_EXCHANGE_FAILED",
                "message": "id_token payload is invalid",
            },
        ) from exc
    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "code": "GATEWAY_OIDC_TOKEN_EXCHANGE_FAILED",
                "message": "id_token payload must be an object",
            },
        )
    return payload


def _subject_uuid(raw_sub: str, *, issuer: str) -> str:
    try:
        return str(UUID(raw_sub.strip()))
    except ValueError:
        return str(uuid5(NAMESPACE_URL, f"{issuer}|{raw_sub.strip()}"))
