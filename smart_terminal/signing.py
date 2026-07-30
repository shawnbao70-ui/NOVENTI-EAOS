"""Terminal Extension signature cryptography (PHX-G44)."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Literal

from kernel.shared.errors import ErrorCode, KernelError
from smart_terminal.models import TerminalExtension

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
class ExtensionSigningSettings:
    mode: SigningMode = "off"
    required: bool = False
    hmac_secret: str | None = None
    ed25519_public_key_pem: str | None = None

    @classmethod
    def from_env(cls) -> ExtensionSigningSettings:
        mode_raw = os.environ.get("EAOS_EXTENSION_SIGNING_MODE", "off").strip().lower()
        mode: SigningMode
        if mode_raw in {"off", "hmac", "ed25519"}:
            mode = mode_raw  # type: ignore[assignment]
        else:
            mode = "off"
        secret = _optional_env("EAOS_EXTENSION_SIGNING_HMAC_SECRET")
        if secret is not None and (len(secret) < 16 or len(secret) > 256):
            raise KernelError(
                ErrorCode.TERMINAL_EXTENSION_SIGNING_UNCONFIGURED,
                "EAOS_EXTENSION_SIGNING_HMAC_SECRET must be 16–256 characters",
            )
        return cls(
            mode=mode,
            required=_env_flag("EAOS_EXTENSION_SIGNING_REQUIRED", default=False),
            hmac_secret=secret,
            ed25519_public_key_pem=_optional_env(
                "EAOS_EXTENSION_SIGNING_ED25519_PUBLIC_KEY_PEM"
            ),
        )

    @classmethod
    def disabled(cls) -> ExtensionSigningSettings:
        return cls(mode="off", required=False)


def canonical_extension_payload(extension: TerminalExtension) -> dict[str, Any]:
    return {
        "allowed_surfaces": sorted(extension.allowed_surfaces),
        "data_scope": extension.data_scope,
        "declared_actions": sorted(extension.declared_actions),
        "declared_capabilities": sorted(extension.declared_capabilities),
        "extension_key": extension.extension_key,
        "tenant_id": str(extension.tenant_id),
        "version": extension.version,
    }


def serialize_extension_signing_body(extension: TerminalExtension) -> bytes:
    payload = canonical_extension_payload(extension)
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


def sign_extension_hmac_v1(*, secret: str, extension: TerminalExtension) -> str:
    body = serialize_extension_signing_body(extension)
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"v1:hmac-sha256:{digest}"


def sign_extension_ed25519_v1(
    *,
    private_key_pem: bytes,
    extension: TerminalExtension,
) -> str:
    private_key = _load_ed25519_private_key(private_key_pem)
    signature = private_key.sign(serialize_extension_signing_body(extension))
    encoded = base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")
    return f"v1:ed25519:{encoded}"


def verify_extension_signature(
    extension: TerminalExtension,
    *,
    signature_ref: str,
    settings: ExtensionSigningSettings,
) -> None:
    cleaned = signature_ref.strip()
    if not cleaned:
        raise KernelError(
            ErrorCode.TERMINAL_EXTENSION_UNSIGNED,
            "signed signature_ref is required",
        )

    if settings.mode == "off":
        if settings.required:
            raise KernelError(
                ErrorCode.TERMINAL_EXTENSION_SIGNING_UNCONFIGURED,
                "extension signing is required but EAOS_EXTENSION_SIGNING_MODE is off",
            )
        return

    if settings.mode == "hmac":
        if not settings.hmac_secret:
            raise KernelError(
                ErrorCode.TERMINAL_EXTENSION_SIGNING_UNCONFIGURED,
                "EAOS_EXTENSION_SIGNING_HMAC_SECRET is required for hmac mode",
            )
        expected = sign_extension_hmac_v1(secret=settings.hmac_secret, extension=extension)
        if not hmac.compare_digest(expected, cleaned):
            raise KernelError(
                ErrorCode.TERMINAL_EXTENSION_SIGNATURE_INVALID,
                "terminal extension HMAC signature is invalid",
            )
        return

    if settings.mode == "ed25519":
        if not settings.ed25519_public_key_pem:
            raise KernelError(
                ErrorCode.TERMINAL_EXTENSION_SIGNING_UNCONFIGURED,
                "EAOS_EXTENSION_SIGNING_ED25519_PUBLIC_KEY_PEM is required for ed25519 mode",
            )
        match = _SIG_REF_RE.match(cleaned)
        if match is None or match.group("alg") != "ed25519":
            raise KernelError(
                ErrorCode.TERMINAL_EXTENSION_SIGNATURE_INVALID,
                "signature_ref must be v1:ed25519:<urlsafe-b64>",
            )
        signature = _b64url_decode(match.group("body"))
        public_key = _load_ed25519_public_key(
            settings.ed25519_public_key_pem.encode("utf-8")
        )
        try:
            public_key.verify(signature, serialize_extension_signing_body(extension))
        except Exception as exc:
            raise KernelError(
                ErrorCode.TERMINAL_EXTENSION_SIGNATURE_INVALID,
                "terminal extension Ed25519 signature is invalid",
            ) from exc
        return

    raise KernelError(
        ErrorCode.TERMINAL_EXTENSION_SIGNING_UNCONFIGURED,
        f"unsupported extension signing mode: {settings.mode}",
    )


def ensure_extension_signature(
    extension: TerminalExtension,
    *,
    settings: ExtensionSigningSettings,
) -> None:
    if not extension.signature_ref:
        raise KernelError(
            ErrorCode.TERMINAL_EXTENSION_UNSIGNED,
            "signed signature_ref is required to activate an extension",
        )
    verify_extension_signature(
        extension,
        signature_ref=extension.signature_ref,
        settings=settings,
    )


def _b64url_decode(value: str) -> bytes:
    padded = value + "=" * (-len(value) % 4)
    try:
        return base64.urlsafe_b64decode(padded.encode("ascii"))
    except Exception as exc:
        raise KernelError(
            ErrorCode.TERMINAL_EXTENSION_SIGNATURE_INVALID,
            "signature_ref body is not valid urlsafe base64",
        ) from exc


def _load_ed25519_private_key(pem: bytes):
    serialization, ed25519 = _require_ed25519()
    key = serialization.load_pem_private_key(pem, password=None)
    if not isinstance(key, ed25519.Ed25519PrivateKey):
        raise KernelError(
            ErrorCode.TERMINAL_EXTENSION_SIGNING_UNCONFIGURED,
            "Ed25519 private key PEM required",
        )
    return key


def _load_ed25519_public_key(pem: bytes):
    serialization, ed25519 = _require_ed25519()
    key = serialization.load_pem_public_key(pem)
    if not isinstance(key, ed25519.Ed25519PublicKey):
        raise KernelError(
            ErrorCode.TERMINAL_EXTENSION_SIGNING_UNCONFIGURED,
            "Ed25519 public key PEM required",
        )
    return key


def _require_ed25519():
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ed25519
    except ImportError as exc:  # pragma: no cover
        raise KernelError(
            ErrorCode.TERMINAL_EXTENSION_SIGNING_UNCONFIGURED,
            "cryptography package required for ed25519 extension signing",
        ) from exc
    return serialization, ed25519
