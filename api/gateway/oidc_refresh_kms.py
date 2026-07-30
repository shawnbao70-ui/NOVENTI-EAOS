"""OIDC refresh KMS key backends (PHX-G75)."""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from typing import Callable, Literal

KmsBackend = Literal["http", "aws", "gcp", "azure"]

_Keys = tuple[str, list[str]]
_FETCH_OVERRIDE: Callable[[], _Keys] | None = None
_CACHE: _Keys | None = None


def configure_kms_keys_fetcher(fetcher: Callable[[], _Keys] | None) -> None:
    """Test helper — None clears override and cache."""

    global _FETCH_OVERRIDE, _CACHE
    _FETCH_OVERRIDE = fetcher
    _CACHE = None


def clear_kms_key_cache() -> None:
    global _CACHE
    _CACHE = None


def refresh_kms_backend() -> KmsBackend:
    raw = (os.environ.get("EAOS_OIDC_REFRESH_KMS_BACKEND") or "").strip().lower()
    if raw in ("http", "aws", "gcp", "azure"):
        return raw  # type: ignore[return-value]
    raise RuntimeError(
        "EAOS_OIDC_REFRESH_KEY_PROVIDER=kms requires "
        "EAOS_OIDC_REFRESH_KMS_BACKEND=http|aws|gcp|azure"
    )


def fetch_kms_fernet_keys() -> _Keys:
    """Return (primary, previous[]) Fernet keys; process-cached."""

    global _CACHE
    if _CACHE is not None:
        return _CACHE
    if _FETCH_OVERRIDE is not None:
        _CACHE = _FETCH_OVERRIDE()
        return _CACHE
    backend = refresh_kms_backend()
    if backend == "http":
        _CACHE = _fetch_http()
    elif backend == "aws":
        _CACHE = _fetch_aws()
    elif backend == "gcp":
        _CACHE = _fetch_gcp()
    else:
        _CACHE = _fetch_azure()
    return _CACHE


def _parse_key_material(raw: str) -> _Keys:
    text = raw.strip()
    if not text:
        raise RuntimeError("KMS key material is empty")
    if text.startswith("{"):
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError("KMS key material JSON is invalid") from exc
        primary = str(payload.get("primary") or "").strip()
        if not primary:
            raise RuntimeError("KMS key material JSON requires primary")
        previous_raw = payload.get("previous") or []
        if not isinstance(previous_raw, list):
            raise RuntimeError("KMS key material JSON previous must be a list")
        previous = [str(item).strip() for item in previous_raw if str(item).strip()]
        return primary, previous
    return text.splitlines()[0].strip(), []


def _ciphertext_bytes() -> bytes:
    raw = (os.environ.get("EAOS_OIDC_REFRESH_KMS_CIPHERTEXT_B64") or "").strip()
    if not raw:
        raise RuntimeError(
            "KMS backend requires EAOS_OIDC_REFRESH_KMS_CIPHERTEXT_B64"
        )
    try:
        return base64.b64decode(raw, validate=True)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            "EAOS_OIDC_REFRESH_KMS_CIPHERTEXT_B64 must be valid base64"
        ) from exc


def _fetch_http() -> _Keys:
    url = (os.environ.get("EAOS_OIDC_REFRESH_KMS_HTTP_URL") or "").strip()
    if not url:
        raise RuntimeError(
            "EAOS_OIDC_REFRESH_KMS_BACKEND=http requires EAOS_OIDC_REFRESH_KMS_HTTP_URL"
        )
    headers: dict[str, str] = {"Accept": "application/json, text/plain"}
    bearer = (os.environ.get("EAOS_OIDC_REFRESH_KMS_HTTP_BEARER") or "").strip()
    if bearer:
        headers["Authorization"] = f"Bearer {bearer}"
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310
            body = response.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise RuntimeError(
            f"EAOS_OIDC_REFRESH_KMS_HTTP_URL fetch failed: {url}"
        ) from exc
    return _parse_key_material(body)


def _fetch_aws() -> _Keys:
    try:
        import boto3  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError(
            "EAOS_OIDC_REFRESH_KMS_BACKEND=aws requires optional dependency boto3"
        ) from exc
    key_id = (os.environ.get("EAOS_OIDC_REFRESH_KMS_KEY_ID") or "").strip()
    if not key_id:
        raise RuntimeError(
            "EAOS_OIDC_REFRESH_KMS_BACKEND=aws requires EAOS_OIDC_REFRESH_KMS_KEY_ID"
        )
    region = (
        os.environ.get("EAOS_OIDC_REFRESH_KMS_REGION")
        or os.environ.get("AWS_REGION")
        or os.environ.get("AWS_DEFAULT_REGION")
        or ""
    ).strip() or None
    client = boto3.client("kms", region_name=region)
    try:
        result = client.decrypt(
            CiphertextBlob=_ciphertext_bytes(),
            KeyId=key_id,
        )
        plaintext = result["Plaintext"]
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("AWS KMS decrypt failed") from exc
    if isinstance(plaintext, bytes):
        return _parse_key_material(plaintext.decode("utf-8"))
    return _parse_key_material(str(plaintext))


def _fetch_gcp() -> _Keys:
    try:
        from google.cloud import kms  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError(
            "EAOS_OIDC_REFRESH_KMS_BACKEND=gcp requires optional dependency google-cloud-kms"
        ) from exc
    key_name = (os.environ.get("EAOS_OIDC_REFRESH_KMS_KEY_NAME") or "").strip()
    if not key_name:
        raise RuntimeError(
            "EAOS_OIDC_REFRESH_KMS_BACKEND=gcp requires EAOS_OIDC_REFRESH_KMS_KEY_NAME"
        )
    client = kms.KeyManagementServiceClient()
    try:
        response = client.decrypt(
            request={"name": key_name, "ciphertext": _ciphertext_bytes()}
        )
        plaintext = response.plaintext
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("GCP Cloud KMS decrypt failed") from exc
    if isinstance(plaintext, bytes):
        return _parse_key_material(plaintext.decode("utf-8"))
    return _parse_key_material(str(plaintext))


def _fetch_azure() -> _Keys:
    try:
        from azure.identity import DefaultAzureCredential  # type: ignore[import-not-found]
        from azure.keyvault.keys.crypto import (  # type: ignore[import-not-found]
            CryptographyClient,
            KeyWrapAlgorithm,
        )
    except ImportError as exc:
        raise RuntimeError(
            "EAOS_OIDC_REFRESH_KMS_BACKEND=azure requires optional dependencies "
            "azure-identity and azure-keyvault-keys"
        ) from exc
    vault_url = (os.environ.get("EAOS_OIDC_REFRESH_KMS_VAULT_URL") or "").strip()
    key_name = (os.environ.get("EAOS_OIDC_REFRESH_KMS_KEY_NAME") or "").strip()
    if not vault_url or not key_name:
        raise RuntimeError(
            "EAOS_OIDC_REFRESH_KMS_BACKEND=azure requires "
            "EAOS_OIDC_REFRESH_KMS_VAULT_URL and EAOS_OIDC_REFRESH_KMS_KEY_NAME"
        )
    key_url = f"{vault_url.rstrip('/')}/keys/{key_name}"
    client = CryptographyClient(key_url, credential=DefaultAzureCredential())
    try:
        result = client.unwrap_key(KeyWrapAlgorithm.rsa_oaep, _ciphertext_bytes())
        plaintext = result.key
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("Azure Key Vault unwrap failed") from exc
    if isinstance(plaintext, bytes):
        return _parse_key_material(plaintext.decode("utf-8"))
    return _parse_key_material(str(plaintext))