"""PHX-G75 OIDC refresh KMS key provider contracts."""

from __future__ import annotations

import base64
import builtins
import json

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

fastapi = pytest.importorskip("fastapi")

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings, clear_jwks_cache, clear_runtime_denylist
from api.gateway.context import configure_jwt_settings
from api.gateway.oidc import clear_oidc_discovery_cache, clear_oidc_states, configure_oidc
from api.gateway.oidc_refresh_crypto import seal_token
from api.gateway.oidc_refresh_kms import (
    configure_kms_keys_fetcher,
    refresh_kms_backend,
)
from api.gateway.oidc_refresh_store import (
    OidcSessionBinding,
    configure_oidc_refresh_store,
    get_oidc_session,
    put_oidc_session,
)

PRIMARY = Fernet.generate_key().decode("ascii")
PREVIOUS = Fernet.generate_key().decode("ascii")


@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "EAOS_OIDC_REFRESH_ENCRYPT",
        "EAOS_OIDC_REFRESH_KEY_PROVIDER",
        "EAOS_OIDC_REFRESH_KMS_BACKEND",
        "EAOS_OIDC_REFRESH_KMS_HTTP_URL",
        "EAOS_OIDC_REFRESH_KMS_HTTP_BEARER",
        "EAOS_OIDC_REFRESH_KMS_CIPHERTEXT_B64",
        "EAOS_OIDC_REFRESH_KMS_KEY_ID",
        "EAOS_OIDC_REFRESH_KMS_KEY_NAME",
        "EAOS_OIDC_REFRESH_KMS_VAULT_URL",
        "EAOS_OIDC_REFRESH_KMS_REGION",
        "EAOS_OIDC_REFRESH_FERNET_KEY",
        "EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS",
        "EAOS_OIDC_REFRESH_REENCRYPT_ON_READ",
    ):
        monkeypatch.delenv(name, raising=False)
    configure_kms_keys_fetcher(None)
    configure_oidc_refresh_store(
        store="memory", encrypt=None, reencrypt_on_read=None, key_provider=None
    )
    clear_oidc_states()
    clear_oidc_discovery_cache()
    clear_runtime_denylist()
    clear_jwks_cache()
    configure_jwt_settings(
        JwtSettings(
            secret="eaos-g75-secret",
            issuer="https://eaos.example/issuer",
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
        )
    )
    configure_oidc(None)
    yield
    configure_kms_keys_fetcher(None)
    clear_oidc_states()
    configure_oidc_refresh_store(
        store="memory", encrypt=None, reencrypt_on_read=None, key_provider=None
    )


def test_kms_requires_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_OIDC_REFRESH_ENCRYPT", "1")
    monkeypatch.setenv("EAOS_OIDC_REFRESH_KEY_PROVIDER", "kms")
    configure_oidc_refresh_store(
        store="memory", encrypt=None, reencrypt_on_read=None, key_provider=None
    )
    with pytest.raises(RuntimeError, match="KMS_BACKEND"):
        seal_token("x")


def test_kms_http_round_trip(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = json.dumps({"primary": PRIMARY, "previous": [PREVIOUS]}).encode("utf-8")

    class _Resp:
        def read(self) -> bytes:
            return payload

        def __enter__(self) -> "_Resp":
            return self

        def __exit__(self, *args: object) -> None:
            return None

    monkeypatch.setenv("EAOS_OIDC_REFRESH_ENCRYPT", "1")
    monkeypatch.setenv("EAOS_OIDC_REFRESH_KEY_PROVIDER", "kms")
    monkeypatch.setenv("EAOS_OIDC_REFRESH_KMS_BACKEND", "http")
    monkeypatch.setenv("EAOS_OIDC_REFRESH_KMS_HTTP_URL", "https://kms.example/fernet")
    monkeypatch.setattr(
        "api.gateway.oidc_refresh_kms.urllib.request.urlopen",
        lambda *args, **kwargs: _Resp(),
    )
    configure_oidc_refresh_store(
        store="memory", encrypt=None, reencrypt_on_read=None, key_provider=None
    )

    put_oidc_session(
        "jti-kms-http",
        OidcSessionBinding(
            refresh_token="refresh-kms-http",
            id_token=None,
            created_at=1.0,
        ),
    )
    assert get_oidc_session("jti-kms-http").refresh_token == "refresh-kms-http"

    client = TestClient(create_app())
    body = client.get("/v1/auth/oidc/status").json()["data"]
    assert body["refresh_encrypt_key_provider"] == "kms"
    assert body["refresh_encrypt_kms_backend"] == "http"
    assert body["refresh_encrypt_key_count"] == 2
    assert PRIMARY not in str(body)
    assert PREVIOUS not in str(body)


def test_kms_aws_without_sdk_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_OIDC_REFRESH_ENCRYPT", "1")
    monkeypatch.setenv("EAOS_OIDC_REFRESH_KEY_PROVIDER", "kms")
    monkeypatch.setenv("EAOS_OIDC_REFRESH_KMS_BACKEND", "aws")
    monkeypatch.setenv("EAOS_OIDC_REFRESH_KMS_KEY_ID", "alias/eaos")
    monkeypatch.setenv(
        "EAOS_OIDC_REFRESH_KMS_CIPHERTEXT_B64",
        base64.b64encode(b"unused").decode("ascii"),
    )
    configure_kms_keys_fetcher(None)
    configure_oidc_refresh_store(
        store="memory", encrypt=None, reencrypt_on_read=None, key_provider=None
    )

    real_import = builtins.__import__

    def _import(name: str, *args: object, **kwargs: object):
        if name == "boto3" or name.startswith("boto3."):
            raise ImportError("boto3 missing for contract")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _import)
    with pytest.raises(RuntimeError, match="boto3"):
        seal_token("x")


def test_kms_cloud_backends_via_fetcher(monkeypatch: pytest.MonkeyPatch) -> None:
    for backend in ("aws", "gcp", "azure"):
        monkeypatch.setenv("EAOS_OIDC_REFRESH_ENCRYPT", "1")
        monkeypatch.setenv("EAOS_OIDC_REFRESH_KEY_PROVIDER", "kms")
        monkeypatch.setenv("EAOS_OIDC_REFRESH_KMS_BACKEND", backend)
        configure_oidc_refresh_store(
            store="memory", encrypt=None, reencrypt_on_read=None, key_provider=None
        )
        configure_kms_keys_fetcher(lambda: (PRIMARY, [PREVIOUS]))
        assert refresh_kms_backend() == backend
        sealed = seal_token("secret-token")
        assert sealed and sealed.startswith("eaos1:")
        put_oidc_session(
            f"jti-{backend}",
            OidcSessionBinding(
                refresh_token="refresh-cloud",
                id_token=None,
                created_at=1.0,
            ),
        )
        assert get_oidc_session(f"jti-{backend}").refresh_token == "refresh-cloud"
        client = TestClient(create_app())
        body = client.get("/v1/auth/oidc/status").json()["data"]
        assert body["refresh_encrypt_kms_backend"] == backend
        assert body["refresh_encrypt_key_count"] == 2
        configure_kms_keys_fetcher(None)