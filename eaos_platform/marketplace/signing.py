"""Marketplace listing signature cryptography (PHX-M18)."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Literal

from eaos_platform.marketplace.models import MarketplaceListing
from kernel.shared.errors import ErrorCode, KernelError

SigningMode = Literal["off", "hmac", "ed25519"]

_SIG_REF_RE = re.compile(
    r"^v1:(?P<alg>hmac-sha256|ed25519):(?P<body>[A-Za-z0-9_\-=+/]+)$"
)


def _env_flag(name: str, *, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _optional_env(name: str) -> str | None:
    value = os.environ.get(name, "").strip()
    return value or None


@dataclass(frozen=True, slots=True)
class MarketplaceSigningSettings:
    mode: SigningMode = "off"
    required: bool = False
    hmac_secret: str | None = None
    ed25519_public_key_pem: str | None = None

    @classmethod
    def from_env(cls) -> MarketplaceSigningSettings:
        mode_raw = os.environ.get("EAOS_MARKETPLACE_SIGNING_MODE", "off").strip().lower()
        mode: SigningMode
        if mode_raw in {"off", "hmac", "ed25519"}:
            mode = mode_raw  # type: ignore[assignment]
        else:
            mode = "off"
        secret = _optional_env("EAOS_MARKETPLACE_SIGNING_HMAC_SECRET")
        if secret is not None and (len(secret) < 16 or len(secret) > 256):
            raise KernelError(
                ErrorCode.MARKETPLACE_SIGNING_UNCONFIGURED,
                "EAOS_MARKETPLACE_SIGNING_HMAC_SECRET must be 16–256 characters",
            )
        return cls(
            mode=mode,
            required=_env_flag("EAOS_MARKETPLACE_SIGNING_REQUIRED", default=False),
            hmac_secret=secret,
            ed25519_public_key_pem=_optional_env(
                "EAOS_MARKETPLACE_SIGNING_ED25519_PUBLIC_KEY_PEM"
            ),
        )

    @classmethod
    def disabled(cls) -> MarketplaceSigningSettings:
        return cls(mode="off", required=False)


def canonical_listing_payload(listing: MarketplaceListing) -> dict[str, Any]:
    return {
        "data_scope": listing.capability.data_scope,
        "declared_events": sorted(listing.capability.declared_events),
        "package_key": listing.package_key,
        "package_version": listing.package_version,
        "publisher_subject_id": str(listing.publisher_subject_id),
        "required_permissions": sorted(listing.capability.required_permissions),
        "tenant_id": str(listing.tenant_id),
    }


def serialize_listing_signing_body(listing: MarketplaceListing) -> bytes:
    payload = canonical_listing_payload(listing)
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


def sign_listing_hmac_v1(*, secret: str, listing: MarketplaceListing) -> str:
    body = serialize_listing_signing_body(listing)
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"v1:hmac-sha256:{digest}"


def sign_listing_ed25519_v1(*, private_key_pem: bytes, listing: MarketplaceListing) -> str:
    private_key = _load_ed25519_private_key(private_key_pem)
    signature = private_key.sign(serialize_listing_signing_body(listing))
    encoded = base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")
    return f"v1:ed25519:{encoded}"


def verify_listing_signature(
    listing: MarketplaceListing,
    *,
    signature_ref: str,
    settings: MarketplaceSigningSettings,
) -> None:
    """Fail-closed verify when signing mode is enabled or required."""

    cleaned = signature_ref.strip()
    if not cleaned:
        raise KernelError(
            ErrorCode.MARKETPLACE_SIGNATURE_REQUIRED,
            "signature_ref is required",
        )

    if settings.mode == "off":
        if settings.required:
            raise KernelError(
                ErrorCode.MARKETPLACE_SIGNING_UNCONFIGURED,
                "marketplace signing is required but EAOS_MARKETPLACE_SIGNING_MODE is off",
            )
        return

    if settings.mode == "hmac":
        if not settings.hmac_secret:
            raise KernelError(
                ErrorCode.MARKETPLACE_SIGNING_UNCONFIGURED,
                "EAOS_MARKETPLACE_SIGNING_HMAC_SECRET is required for hmac mode",
            )
        expected = sign_listing_hmac_v1(secret=settings.hmac_secret, listing=listing)
        if not hmac.compare_digest(expected, cleaned):
            raise KernelError(
                ErrorCode.MARKETPLACE_SIGNATURE_INVALID,
                "marketplace listing HMAC signature is invalid",
            )
        return

    if settings.mode == "ed25519":
        if not settings.ed25519_public_key_pem:
            raise KernelError(
                ErrorCode.MARKETPLACE_SIGNING_UNCONFIGURED,
                "EAOS_MARKETPLACE_SIGNING_ED25519_PUBLIC_KEY_PEM is required for ed25519 mode",
            )
        match = _SIG_REF_RE.match(cleaned)
        if match is None or match.group("alg") != "ed25519":
            raise KernelError(
                ErrorCode.MARKETPLACE_SIGNATURE_INVALID,
                "signature_ref must be v1:ed25519:<urlsafe-b64>",
            )
        signature = _b64url_decode(match.group("body"))
        public_key = _load_ed25519_public_key(settings.ed25519_public_key_pem.encode("utf-8"))
        try:
            public_key.verify(signature, serialize_listing_signing_body(listing))
        except Exception as exc:  # InvalidSignature and friends
            raise KernelError(
                ErrorCode.MARKETPLACE_SIGNATURE_INVALID,
                "marketplace listing Ed25519 signature is invalid",
            ) from exc
        return

    raise KernelError(
        ErrorCode.MARKETPLACE_SIGNING_UNCONFIGURED,
        f"unsupported marketplace signing mode: {settings.mode}",
    )


def ensure_listing_signature(
    listing: MarketplaceListing,
    *,
    settings: MarketplaceSigningSettings,
) -> None:
    """Re-check stored signature_ref under current settings."""

    if not listing.signature_ref:
        raise KernelError(
            ErrorCode.MARKETPLACE_SIGNATURE_REQUIRED,
            "signature_ref is required",
        )
    verify_listing_signature(
        listing,
        signature_ref=listing.signature_ref,
        settings=settings,
    )


def _b64url_decode(value: str) -> bytes:
    padded = value + "=" * (-len(value) % 4)
    try:
        return base64.urlsafe_b64decode(padded.encode("ascii"))
    except Exception as exc:
        raise KernelError(
            ErrorCode.MARKETPLACE_SIGNATURE_INVALID,
            "signature_ref body is not valid urlsafe base64",
        ) from exc


def _load_ed25519_private_key(pem: bytes):
    serialization, ed25519 = _require_ed25519()
    key = serialization.load_pem_private_key(pem, password=None)
    if not isinstance(key, ed25519.Ed25519PrivateKey):
        raise KernelError(
            ErrorCode.MARKETPLACE_SIGNING_UNCONFIGURED,
            "Ed25519 private key PEM required",
        )
    return key


def _load_ed25519_public_key(pem: bytes):
    serialization, ed25519 = _require_ed25519()
    key = serialization.load_pem_public_key(pem)
    if not isinstance(key, ed25519.Ed25519PublicKey):
        raise KernelError(
            ErrorCode.MARKETPLACE_SIGNING_UNCONFIGURED,
            "Ed25519 public key PEM required",
        )
    return key


def _require_ed25519():
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ed25519
    except ImportError as exc:  # pragma: no cover
        raise KernelError(
            ErrorCode.MARKETPLACE_SIGNING_UNCONFIGURED,
            "cryptography package required for ed25519 marketplace signing",
        ) from exc
    return serialization, ed25519
