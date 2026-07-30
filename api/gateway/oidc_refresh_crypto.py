"""OIDC refresh token field encryption + key ring + providers (PHX-G64/G65/G70/G74/G75)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from api.gateway.oidc_refresh_kms import (
    clear_kms_key_cache,
    fetch_kms_fernet_keys,
)

EncryptLabel = Literal["off", "fernet"]
KeyProvider = Literal["env", "file", "kms"]

_CIPHER_PREFIX = "eaos1:"
_ENCRYPT_OVERRIDE: bool | None = None
_REENCRYPT_OVERRIDE: bool | None = None
_PROVIDER_OVERRIDE: KeyProvider | None = None


def configure_oidc_refresh_encrypt(
    *,
    enabled: bool | None = None,
    reencrypt_on_read: bool | None = None,
    key_provider: KeyProvider | None = None,
) -> None:
    """Test helper — None clears override (fall back to env)."""

    global _ENCRYPT_OVERRIDE, _REENCRYPT_OVERRIDE, _PROVIDER_OVERRIDE
    _ENCRYPT_OVERRIDE = enabled
    _REENCRYPT_OVERRIDE = reencrypt_on_read
    _PROVIDER_OVERRIDE = key_provider
    clear_kms_key_cache()


def refresh_encrypt_enabled() -> bool:
    if _ENCRYPT_OVERRIDE is not None:
        return _ENCRYPT_OVERRIDE
    raw = (os.environ.get("EAOS_OIDC_REFRESH_ENCRYPT") or "0").strip().lower()
    return raw in ("1", "true", "yes", "on")


def refresh_reencrypt_on_read_enabled() -> bool:
    if _REENCRYPT_OVERRIDE is not None:
        return _REENCRYPT_OVERRIDE
    raw = (os.environ.get("EAOS_OIDC_REFRESH_REENCRYPT_ON_READ") or "0").strip().lower()
    return raw in ("1", "true", "yes", "on")


def refresh_key_provider() -> KeyProvider:
    if _PROVIDER_OVERRIDE is not None:
        return _PROVIDER_OVERRIDE
    raw = (os.environ.get("EAOS_OIDC_REFRESH_KEY_PROVIDER") or "env").strip().lower()
    if raw in ("", "env"):
        return "env"
    if raw == "file":
        return "file"
    if raw == "kms":
        return "kms"
    raise RuntimeError("EAOS_OIDC_REFRESH_KEY_PROVIDER must be env, file, or kms")


def refresh_encrypt_kms_backend_label() -> str | None:
    """Status label — does not validate backend (fetch path fail-closes)."""

    if refresh_key_provider() != "kms":
        return None
    raw = (os.environ.get("EAOS_OIDC_REFRESH_KMS_BACKEND") or "").strip().lower()
    return raw or None


def refresh_encrypt_label() -> EncryptLabel:
    return "fernet" if refresh_encrypt_enabled() else "off"


def refresh_encrypt_key_count() -> int:
    if not refresh_encrypt_enabled():
        return 0
    return len(_fernet_keys())


def seal_token(value: str | None) -> str | None:
    if value is None:
        return None
    if not refresh_encrypt_enabled():
        return value
    token = _multi_fernet().encrypt(value.encode("utf-8")).decode("ascii")
    return f"{_CIPHER_PREFIX}{token}"


def open_token(value: str | None) -> str | None:
    if value is None:
        return None
    if value.startswith(_CIPHER_PREFIX):
        cipher = value[len(_CIPHER_PREFIX) :]
        return _multi_fernet().decrypt(cipher.encode("ascii")).decode("utf-8")
    if refresh_encrypt_enabled():
        raise RuntimeError(
            "EAOS_OIDC_REFRESH_ENCRYPT requires eaos1: ciphertext in stored tokens"
        )
    return value


def ciphertext_needs_primary_rotation(value: str | None) -> bool:
    """True when ciphertext is not decryptable by the primary key alone."""

    if value is None or not value.startswith(_CIPHER_PREFIX):
        return False
    if not refresh_encrypt_enabled():
        return False
    from cryptography.fernet import Fernet, InvalidToken

    cipher = value[len(_CIPHER_PREFIX) :].encode("ascii")
    try:
        Fernet(_primary_key().encode("ascii")).decrypt(cipher)
        return False
    except InvalidToken:
        try:
            _multi_fernet().decrypt(cipher)
        except InvalidToken:
            return False
        return True
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            "EAOS_OIDC_REFRESH Fernet keys must be valid Fernet keys"
        ) from exc


def _primary_key() -> str:
    provider = refresh_key_provider()
    if provider == "kms":
        return fetch_kms_fernet_keys()[0]
    if provider == "file":
        path = (os.environ.get("EAOS_OIDC_REFRESH_FERNET_KEY_FILE") or "").strip()
        if not path:
            raise RuntimeError(
                "EAOS_OIDC_REFRESH_KEY_PROVIDER=file requires EAOS_OIDC_REFRESH_FERNET_KEY_FILE"
            )
        try:
            key = Path(path).read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise RuntimeError(
                f"EAOS_OIDC_REFRESH_FERNET_KEY_FILE is unreadable: {path}"
            ) from exc
        if not key:
            raise RuntimeError("EAOS_OIDC_REFRESH_FERNET_KEY_FILE is empty")
        return key
    key = (os.environ.get("EAOS_OIDC_REFRESH_FERNET_KEY") or "").strip()
    if not key:
        raise RuntimeError(
            "EAOS_OIDC_REFRESH_ENCRYPT requires EAOS_OIDC_REFRESH_FERNET_KEY"
        )
    return key


def _previous_keys() -> list[str]:
    keys: list[str] = []
    if refresh_key_provider() == "kms":
        keys.extend(fetch_kms_fernet_keys()[1])
    file_path = (os.environ.get("EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS_FILE") or "").strip()
    if file_path:
        try:
            text = Path(file_path).read_text(encoding="utf-8")
        except OSError as exc:
            raise RuntimeError(
                f"EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS_FILE is unreadable: {file_path}"
            ) from exc
        keys.extend(
            [
                line.strip()
                for line in text.splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]
        )
        return keys
    raw = (os.environ.get("EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS") or "").strip()
    if raw:
        keys.extend([part.strip() for part in raw.split(",") if part.strip()])
    return keys


def _fernet_keys() -> list[str]:
    return [_primary_key(), *_previous_keys()]


def _multi_fernet():
    from cryptography.fernet import Fernet, MultiFernet

    fernets: list = []
    for key in _fernet_keys():
        try:
            fernets.append(Fernet(key.encode("ascii")))
        except Exception as exc:  # noqa: BLE001 — surface Fernet key errors uniformly
            raise RuntimeError(
                "EAOS_OIDC_REFRESH Fernet keys must be valid Fernet keys"
            ) from exc
    return MultiFernet(fernets)
