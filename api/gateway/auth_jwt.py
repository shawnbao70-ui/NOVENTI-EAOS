"""JWT verification for Gateway trusted context (G37/G38/G45)."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from fastapi import HTTPException, status

from kernel.shared.context import ExecutionContext, SubjectType

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding, rsa
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
except ImportError:  # pragma: no cover - exercised when api extra incomplete
    hashes = None  # type: ignore[assignment]
    serialization = None  # type: ignore[assignment]
    padding = None  # type: ignore[assignment]
    rsa = None  # type: ignore[assignment]
    RSAPublicNumbers = None  # type: ignore[assignment]

_JWKS_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
_DENYLIST_CACHE: dict[str, tuple[float, list[Any]]] = {}
# Process-local JWT revoke set (PHX-G61 logout): (jti, iss|None)
_RUNTIME_DENYLIST: set[tuple[str, str | None]] = set()


@dataclass(frozen=True, slots=True)
class JwtIssuerBinding:
    """Per-issuer JWKS binding (PHX-G45)."""

    issuer: str
    jwks_json: str | None = None
    jwks_url: str | None = None


@dataclass(frozen=True, slots=True)
class JwtSettings:
    secret: str
    issuer: str | None
    audience: str | None
    allow_dev_headers: bool
    require_jwt: bool
    jwks_json: str | None = None
    jwks_url: str | None = None
    leeway_seconds: int = 30
    jwks_cache_seconds: int = 300
    issuers: tuple[JwtIssuerBinding, ...] = field(default_factory=tuple)
    denylist_json: str | None = None
    denylist_url: str | None = None
    denylist_cache_seconds: int = 60

    @property
    def multi_issuer(self) -> bool:
        return bool(self.issuers)

    @property
    def denylist_enabled(self) -> bool:
        return bool(self.denylist_json or self.denylist_url)

    @classmethod
    def from_env(cls) -> JwtSettings:
        secret = os.environ.get("EAOS_JWT_SECRET", "").strip()
        return cls(
            secret=secret,
            issuer=_optional_env("EAOS_JWT_ISSUER"),
            audience=_optional_env("EAOS_JWT_AUDIENCE"),
            allow_dev_headers=_env_flag("EAOS_ALLOW_DEV_CONTEXT_HEADERS", default=True),
            require_jwt=_env_flag("EAOS_REQUIRE_JWT", default=False),
            jwks_json=_optional_env("EAOS_JWT_JWKS_JSON"),
            jwks_url=_optional_env("EAOS_JWT_JWKS_URL"),
            issuers=_parse_issuers_json(_optional_env("EAOS_JWT_ISSUERS_JSON")),
            denylist_json=_optional_env("EAOS_JWT_DENYLIST_JSON"),
            denylist_url=_optional_env("EAOS_JWT_DENYLIST_URL"),
        )


def mint_hs256_token(
    claims: dict[str, Any],
    *,
    secret: str,
    headers: dict[str, str] | None = None,
) -> str:
    """Test/helper mint — not an IdP."""

    header = {"alg": "HS256", "typ": "JWT"}
    if headers:
        header.update(headers)
    signing_input = f"{_b64url_json(header)}.{_b64url_json(claims)}".encode("ascii")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{signing_input.decode('ascii')}.{_b64url(signature)}"


def mint_rs256_token(
    claims: dict[str, Any],
    *,
    private_key_pem: bytes,
    kid: str | None = None,
    headers: dict[str, str] | None = None,
) -> str:
    """Test/helper RS256 mint — requires cryptography."""

    _require_cryptography()
    assert serialization is not None and padding is not None and hashes is not None
    private_key = serialization.load_pem_private_key(private_key_pem, password=None)
    header: dict[str, Any] = {"alg": "RS256", "typ": "JWT"}
    if kid:
        header["kid"] = kid
    if headers:
        header.update(headers)
    signing_input = f"{_b64url_json(header)}.{_b64url_json(claims)}".encode("ascii")
    signature = private_key.sign(  # type: ignore[union-attr]
        signing_input,
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return f"{signing_input.decode('ascii')}.{_b64url(signature)}"


def verify_hs256_token(token: str, settings: JwtSettings) -> dict[str, Any]:
    """Backward-compatible alias — prefers verify_token."""

    return verify_token(token, settings)


def verify_token(token: str, settings: JwtSettings) -> dict[str, Any]:
    parts = token.split(".")
    if len(parts) != 3:
        raise _unauthorized("JWT must have three segments")
    header_b64, payload_b64, sig_b64 = parts
    try:
        header = _b64url_json_decode(header_b64)
        payload = _b64url_json_decode(payload_b64)
        signature = _b64url_decode(sig_b64)
    except (ValueError, json.JSONDecodeError) as exc:
        raise _unauthorized("JWT encoding is invalid") from exc

    alg = str(header.get("alg") or "")
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    issuer_binding: JwtIssuerBinding | None = None
    if settings.multi_issuer:
        issuer_binding = _resolve_issuer_binding(payload, settings)
    if alg == "HS256":
        _verify_hs256(signing_input, signature, settings)
    elif alg == "RS256":
        _verify_rs256(
            signing_input,
            signature,
            header,
            settings,
            issuer_binding=issuer_binding,
        )
    else:
        raise _unauthorized("unsupported JWT alg")

    _validate_time_and_party(payload, settings, issuer_binding=issuer_binding)
    if not isinstance(payload, dict):
        raise _unauthorized("JWT payload must be an object")
    _enforce_denylist(payload, settings)
    return payload


def _roles_from_eaos_claims(claims: dict[str, Any]) -> tuple[str, ...]:
    """Parse JWT ``eaos_roles`` into sorted unique roles (PHX-G82).

    Missing/null → empty. Wrong type or non-string elements → CTX_INVALID.
    """

    raw = claims.get("eaos_roles")
    if raw is None:
        return ()
    if not isinstance(raw, (list, tuple)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "CTX_INVALID",
                "message": "eaos_roles must be an array of strings",
            },
        )
    normalized: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "CTX_INVALID",
                    "message": "eaos_roles must be an array of strings",
                },
            )
        value = item.strip()
        if value:
            normalized.append(value)
    return tuple(sorted(set(normalized)))


def context_from_tenant_claims(
    claims: dict[str, Any],
    *,
    correlation_header: str | None,
    eaos_jwt_issuer: str | None = None,
) -> ExecutionContext:
    if claims.get("eaos_platform_scope") is True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "CTX_PLATFORM_ELEVATION_DENIED",
                "message": "platform_scope JWT cannot be used on the tenant plane",
            },
        )
    subject_id = _require_uuid_claim(claims, "sub", code="CTX_MISSING_SUBJECT")
    tenant_raw = claims.get("eaos_tenant_id")
    if tenant_raw is None or str(tenant_raw).strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "CTX_MISSING_TENANT",
                "message": "eaos_tenant_id claim is required",
            },
        )
    try:
        tenant_id = UUID(str(tenant_raw).strip())
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "CTX_INVALID",
                "message": "eaos_tenant_id must be a UUID",
            },
        ) from exc
    from api.gateway.tenant_idp_federation import (
        assert_tenant_idp_binding,
        resolve_federation_issuer,
    )

    assert_tenant_idp_binding(
        tenant_id=tenant_id,
        issuer=resolve_federation_issuer(
            claims, eaos_jwt_issuer=eaos_jwt_issuer
        ),
    )
    subject_type = _subject_type(claims.get("eaos_subject_type"))
    correlation = _correlation_id(claims, correlation_header)
    roles = _roles_from_eaos_claims(claims)
    return ExecutionContext(
        subject_id=subject_id,
        subject_type=subject_type,
        tenant_id=tenant_id,
        platform_scope=False,
        correlation_id=correlation,
        request_time=ExecutionContext.utc_now(),
        roles=roles,
    )


def context_from_platform_claims(
    claims: dict[str, Any],
    *,
    correlation_header: str | None,
) -> ExecutionContext:
    if claims.get("eaos_platform_scope") is not True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "CTX_PLATFORM_SCOPE_REQUIRED",
                "message": "eaos_platform_scope=true claim is required for platform plane",
            },
        )
    subject_id = _require_uuid_claim(claims, "sub", code="CTX_MISSING_SUBJECT")
    subject_type = _subject_type(claims.get("eaos_subject_type") or SubjectType.SERVICE.value)
    correlation = _correlation_id(claims, correlation_header)
    return ExecutionContext(
        subject_id=subject_id,
        subject_type=subject_type,
        tenant_id=None,
        platform_scope=True,
        correlation_id=correlation,
        request_time=ExecutionContext.utc_now(),
    )


def extract_bearer(authorization: str | None) -> str | None:
    if not isinstance(authorization, str) or not authorization.strip():
        return None
    scheme, _, token = authorization.strip().partition(" ")
    if scheme.casefold() != "bearer" or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "GATEWAY_AUTH_INVALID",
                "message": "Authorization must be Bearer <token>",
            },
        )
    return token.strip()


def clear_jwks_cache() -> None:
    """Test helper."""

    _JWKS_CACHE.clear()


def clear_denylist_cache() -> None:
    """Test helper."""

    _DENYLIST_CACHE.clear()


def revoke_runtime_jti(jti: str, *, iss: str | None = None) -> None:
    """Revoke a JWT jti in-process (PHX-G61 logout)."""

    cleaned = (jti or "").strip()
    if not cleaned:
        return
    iss_value = (iss or "").strip() or None
    _RUNTIME_DENYLIST.add((cleaned, iss_value))


def clear_runtime_denylist() -> None:
    """Test helper."""

    _RUNTIME_DENYLIST.clear()


def runtime_denylist_count() -> int:
    """Process-local revoked jti count (PHX-G96)."""

    return len(_RUNTIME_DENYLIST)


def jwt_status_view(settings: JwtSettings | None = None) -> dict[str, Any]:
    """Redacted JWT / denylist observability (PHX-G96); never lists jtis."""

    active = settings if settings is not None else JwtSettings.from_env()
    configured_entry_count: int | None = None
    load_error: str | None = None
    if active.denylist_enabled:
        try:
            configured_entry_count = len(_load_denylist(active))
        except HTTPException as exc:
            detail = exc.detail
            if isinstance(detail, dict):
                load_error = str(detail.get("code") or detail.get("message") or "load_failed")
            else:
                load_error = "load_failed"
    denylist: dict[str, Any] = {
        "enabled": active.denylist_enabled,
        "has_json": bool(active.denylist_json),
        "has_url": bool(active.denylist_url),
        "cache_seconds": active.denylist_cache_seconds,
        "configured_entry_count": configured_entry_count,
        "load_error": load_error,
        "runtime_revoked_count": runtime_denylist_count(),
    }
    if active.denylist_url:
        denylist["url"] = active.denylist_url.strip()
    return {
        "writable": False,
        "secrets_exposed": False,
        "production_auth_fail_closed": True,
        "require_jwt": active.require_jwt,
        "allow_dev_headers": active.allow_dev_headers,
        "multi_issuer": active.multi_issuer,
        "issuer": active.issuer,
        "audience": active.audience,
        "has_secret": bool(active.secret),
        "has_jwks_url": bool(active.jwks_url),
        "has_jwks_json": bool(active.jwks_json),
        "issuer_count": len(active.issuers),
        "denylist": denylist,
    }


def jwk_from_rsa_public_numbers(*, n: int, e: int, kid: str) -> dict[str, str]:
    """Build a public JWK dict for tests."""

    return {
        "kty": "RSA",
        "kid": kid,
        "use": "sig",
        "alg": "RS256",
        "n": _b64url(_int_to_bytes(n)),
        "e": _b64url(_int_to_bytes(e)),
    }


def _verify_hs256(signing_input: bytes, signature: bytes, settings: JwtSettings) -> None:
    if not settings.secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_JWT_UNCONFIGURED",
                "message": "EAOS_JWT_SECRET is not configured for HS256",
            },
        )
    expected = hmac.new(
        settings.secret.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    if not hmac.compare_digest(signature, expected):
        raise _unauthorized("JWT signature is invalid")


def _verify_rs256(
    signing_input: bytes,
    signature: bytes,
    header: dict[str, Any],
    settings: JwtSettings,
    *,
    issuer_binding: JwtIssuerBinding | None = None,
) -> None:
    _require_cryptography()
    assert padding is not None and hashes is not None
    jwks_json, jwks_url = _jwks_sources(settings, issuer_binding)
    if not jwks_json and not jwks_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_JWT_UNCONFIGURED",
                "message": "JWKS JSON or URL is required for RS256",
            },
        )
    jwks = _load_jwks(
        jwks_json=jwks_json,
        jwks_url=jwks_url,
        cache_seconds=settings.jwks_cache_seconds,
    )
    selected = _select_rsa_jwk(jwks, header.get("kid"))
    if selected is None and jwks_url:
        # Key rotation window: bypass cache once when kid is missing.
        jwks = _load_jwks(
            jwks_json=None,
            jwks_url=jwks_url,
            cache_seconds=settings.jwks_cache_seconds,
            force_refresh=True,
        )
        selected = _select_rsa_jwk(jwks, header.get("kid"))
    if selected is None:
        raise _unauthorized("JWT kid not found in JWKS")
    public_key = _rsa_public_key_from_jwk(selected)
    try:
        public_key.verify(signature, signing_input, padding.PKCS1v15(), hashes.SHA256())
    except Exception as exc:
        raise _unauthorized("JWT signature is invalid") from exc


def _jwks_sources(
    settings: JwtSettings,
    issuer_binding: JwtIssuerBinding | None,
) -> tuple[str | None, str | None]:
    if issuer_binding is not None:
        return issuer_binding.jwks_json, issuer_binding.jwks_url
    return settings.jwks_json, settings.jwks_url


def _select_rsa_jwk(jwks: dict[str, Any], kid: Any) -> dict[str, Any] | None:
    keys = [
        key
        for key in jwks.get("keys", [])
        if isinstance(key, dict) and key.get("kty") == "RSA"
    ]
    if not keys:
        raise _unauthorized("JWKS contains no RSA keys")
    if kid is not None and str(kid).strip():
        for key in keys:
            if key.get("kid") == kid:
                return key
        return None
    if len(keys) == 1:
        return keys[0]
    raise _unauthorized("JWT kid is required when JWKS has multiple keys")


def _load_jwks(
    *,
    jwks_json: str | None,
    jwks_url: str | None,
    cache_seconds: int,
    force_refresh: bool = False,
) -> dict[str, Any]:
    if jwks_json:
        try:
            document = json.loads(jwks_json)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "GATEWAY_JWT_UNCONFIGURED",
                    "message": "JWKS JSON is invalid",
                },
            ) from exc
        if not isinstance(document, dict):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "GATEWAY_JWT_UNCONFIGURED",
                    "message": "JWKS document must be an object",
                },
            )
        return document

    assert jwks_url is not None
    url = jwks_url.strip()
    if not url.casefold().startswith("https://"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_JWT_UNCONFIGURED",
                "message": "JWKS URL must use https",
            },
        )
    now = time.time()
    if force_refresh:
        _JWKS_CACHE.pop(url, None)
    cached = _JWKS_CACHE.get(url)
    if cached is not None and cached[0] > now:
        return cached[1]
    try:
        with urllib.request.urlopen(url, timeout=5) as response:  # noqa: S310
            raw = response.read()
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_JWT_UNCONFIGURED",
                "message": "failed to fetch JWKS URL",
            },
        ) from exc
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_JWT_UNCONFIGURED",
                "message": "JWKS URL returned invalid JSON",
            },
        ) from exc
    if not isinstance(document, dict):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_JWT_UNCONFIGURED",
                "message": "JWKS document must be an object",
            },
        )
    _JWKS_CACHE[url] = (now + max(1, cache_seconds), document)
    return document


def _rsa_public_key_from_jwk(jwk: dict[str, Any]):
    _require_cryptography()
    assert RSAPublicNumbers is not None
    try:
        n = int.from_bytes(_b64url_decode(str(jwk["n"])), "big")
        e = int.from_bytes(_b64url_decode(str(jwk["e"])), "big")
    except (KeyError, ValueError) as exc:
        raise _unauthorized("JWKS RSA key is invalid") from exc
    return RSAPublicNumbers(e, n).public_key()


def _resolve_issuer_binding(
    payload: dict[str, Any],
    settings: JwtSettings,
) -> JwtIssuerBinding:
    iss = payload.get("iss")
    if iss is None or not str(iss).strip():
        raise _unauthorized("JWT issuer is required")
    issuer = str(iss).strip()
    for binding in settings.issuers:
        if binding.issuer == issuer:
            return binding
    raise _unauthorized("JWT issuer is not allowlisted")


def _parse_issuers_json(raw: str | None) -> tuple[JwtIssuerBinding, ...]:
    if raw is None:
        return ()
    try:
        document = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_JWT_UNCONFIGURED",
                "message": "EAOS_JWT_ISSUERS_JSON is invalid JSON",
            },
        ) from exc
    if not isinstance(document, list) or not document:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_JWT_UNCONFIGURED",
                "message": "EAOS_JWT_ISSUERS_JSON must be a non-empty array",
            },
        )
    bindings: list[JwtIssuerBinding] = []
    seen: set[str] = set()
    for item in document:
        if not isinstance(item, dict):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "GATEWAY_JWT_UNCONFIGURED",
                    "message": "each issuer binding must be an object",
                },
            )
        issuer = str(item.get("issuer") or "").strip()
        jwks_json = item.get("jwks_json")
        jwks_url = item.get("jwks_url")
        jwks_json_s = str(jwks_json).strip() if jwks_json is not None else None
        jwks_url_s = str(jwks_url).strip() if jwks_url is not None else None
        if not issuer:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "GATEWAY_JWT_UNCONFIGURED",
                    "message": "issuer binding requires issuer",
                },
            )
        if not jwks_json_s and not jwks_url_s:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "GATEWAY_JWT_UNCONFIGURED",
                    "message": f"issuer {issuer} requires jwks_json or jwks_url",
                },
            )
        if issuer in seen:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "GATEWAY_JWT_UNCONFIGURED",
                    "message": f"duplicate issuer binding: {issuer}",
                },
            )
        seen.add(issuer)
        bindings.append(
            JwtIssuerBinding(
                issuer=issuer,
                jwks_json=jwks_json_s or None,
                jwks_url=jwks_url_s or None,
            )
        )
    return tuple(bindings)


def _validate_time_and_party(
    payload: dict[str, Any],
    settings: JwtSettings,
    *,
    issuer_binding: JwtIssuerBinding | None = None,
) -> None:
    now = int(time.time())
    exp = payload.get("exp")
    if exp is not None:
        try:
            if now > int(exp) + settings.leeway_seconds:
                raise _unauthorized("JWT has expired")
        except (TypeError, ValueError) as exc:
            raise _unauthorized("JWT exp claim is invalid") from exc
    nbf = payload.get("nbf")
    if nbf is not None:
        try:
            if now + settings.leeway_seconds < int(nbf):
                raise _unauthorized("JWT is not yet valid")
        except (TypeError, ValueError) as exc:
            raise _unauthorized("JWT nbf claim is invalid") from exc
    if issuer_binding is not None:
        if payload.get("iss") != issuer_binding.issuer:
            raise _unauthorized("JWT issuer is invalid")
    elif settings.issuer is not None and payload.get("iss") != settings.issuer:
        raise _unauthorized("JWT issuer is invalid")
    if settings.audience is not None:
        aud = payload.get("aud")
        audiences = aud if isinstance(aud, list) else [aud]
        if settings.audience not in audiences:
            raise _unauthorized("JWT audience is invalid")


def _require_cryptography() -> None:
    if (
        hashes is None
        or serialization is None
        or padding is None
        or rsa is None
        or RSAPublicNumbers is None
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_JWT_UNCONFIGURED",
                "message": "cryptography package is required for RS256/JWKS",
            },
        )


def _optional_env(name: str) -> str | None:
    value = os.environ.get(name, "").strip()
    return value or None


def _env_flag(name: str, *, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    return str(raw).strip().casefold() in {"1", "true", "yes", "on"}


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_json(value: dict[str, Any]) -> str:
    return _b64url(json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8"))


def _b64url_decode(segment: str) -> bytes:
    padding_chars = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding_chars)


def _b64url_json_decode(segment: str) -> dict[str, Any]:
    raw = _b64url_decode(segment)
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JWT JSON must be an object")
    return value


def _int_to_bytes(value: int) -> bytes:
    length = max(1, (value.bit_length() + 7) // 8)
    return value.to_bytes(length, "big")


def _enforce_denylist(payload: dict[str, Any], settings: JwtSettings) -> None:
    jti = payload.get("jti")
    if jti is None or not str(jti).strip():
        return
    jti_value = str(jti).strip()
    iss_value = str(payload.get("iss") or "").strip() or None
    if (jti_value, iss_value) in _RUNTIME_DENYLIST or (jti_value, None) in _RUNTIME_DENYLIST:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "GATEWAY_JWT_REVOKED",
                "message": "JWT has been revoked",
            },
        )
    if not settings.denylist_enabled:
        return
    now = int(time.time())
    for entry in _load_denylist(settings):
        denied_jti, denied_iss, entry_exp = _normalize_denylist_entry(entry)
        if denied_jti is None:
            continue
        if entry_exp is not None and now > entry_exp:
            continue
        if denied_jti != jti_value:
            continue
        if denied_iss is not None and denied_iss != iss_value:
            continue
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "GATEWAY_JWT_REVOKED",
                "message": "JWT has been revoked",
            },
        )


def _normalize_denylist_entry(
    entry: Any,
) -> tuple[str | None, str | None, int | None]:
    if isinstance(entry, str):
        cleaned = entry.strip()
        return (cleaned or None, None, None)
    if not isinstance(entry, dict):
        return (None, None, None)
    jti = str(entry.get("jti") or "").strip() or None
    iss = str(entry.get("iss") or "").strip() or None
    exp_raw = entry.get("exp")
    exp: int | None
    if exp_raw is None or str(exp_raw).strip() == "":
        exp = None
    else:
        try:
            exp = int(exp_raw)
        except (TypeError, ValueError):
            exp = None
    return jti, iss, exp


def _load_denylist(settings: JwtSettings) -> list[Any]:
    if settings.denylist_json:
        try:
            document = json.loads(settings.denylist_json)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "GATEWAY_JWT_UNCONFIGURED",
                    "message": "EAOS_JWT_DENYLIST_JSON is invalid JSON",
                },
            ) from exc
        if not isinstance(document, list):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "GATEWAY_JWT_UNCONFIGURED",
                    "message": "denylist document must be an array",
                },
            )
        return document

    assert settings.denylist_url is not None
    url = settings.denylist_url.strip()
    if not url.casefold().startswith("https://"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_JWT_UNCONFIGURED",
                "message": "EAOS_JWT_DENYLIST_URL must use https",
            },
        )
    now = time.time()
    cached = _DENYLIST_CACHE.get(url)
    if cached is not None and cached[0] > now:
        return cached[1]
    try:
        with urllib.request.urlopen(url, timeout=5) as response:  # noqa: S310
            raw = response.read()
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_JWT_UNCONFIGURED",
                "message": "failed to fetch JWT denylist URL",
            },
        ) from exc
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_JWT_UNCONFIGURED",
                "message": "denylist URL returned invalid JSON",
            },
        ) from exc
    if not isinstance(document, list):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "GATEWAY_JWT_UNCONFIGURED",
                "message": "denylist document must be an array",
            },
        )
    _DENYLIST_CACHE[url] = (now + max(1, settings.denylist_cache_seconds), document)
    return document


def _unauthorized(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "GATEWAY_JWT_INVALID", "message": message},
    )


def _require_uuid_claim(claims: dict[str, Any], name: str, *, code: str) -> UUID:
    raw = claims.get(name)
    if raw is None or str(raw).strip() == "":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": code, "message": f"{name} claim is required"},
        )
    try:
        return UUID(str(raw).strip())
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "CTX_INVALID", "message": f"{name} must be a UUID"},
        ) from exc


def _subject_type(raw: Any) -> SubjectType:
    value = str(raw or SubjectType.HUMAN.value).strip().casefold()
    try:
        return SubjectType(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "CTX_INVALID",
                "message": "eaos_subject_type claim is invalid",
            },
        ) from exc


def _correlation_id(claims: dict[str, Any], header: str | None) -> str:
    if header and header.strip():
        return header.strip()
    jti = claims.get("jti")
    if jti is not None and str(jti).strip():
        return str(jti).strip()
    return str(uuid4())
