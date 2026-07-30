"""PHX-G70 OIDC refresh re-encrypt on read contracts."""

from __future__ import annotations

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

fastapi = pytest.importorskip("fastapi")

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings, clear_jwks_cache, clear_runtime_denylist
from api.gateway.context import configure_jwt_settings
from api.gateway.oidc import clear_oidc_discovery_cache, clear_oidc_states, configure_oidc
from api.gateway.oidc_refresh_crypto import (
    ciphertext_needs_primary_rotation,
    refresh_reencrypt_on_read_enabled,
)
from api.gateway.oidc_refresh_store import (
    OidcSessionBinding,
    _SESSIONS,
    configure_oidc_refresh_store,
    get_oidc_session,
    put_oidc_session,
)

OLD_KEY = Fernet.generate_key().decode("ascii")
NEW_KEY = Fernet.generate_key().decode("ascii")


@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EAOS_OIDC_REFRESH_ENCRYPT", raising=False)
    monkeypatch.delenv("EAOS_OIDC_REFRESH_REENCRYPT_ON_READ", raising=False)
    monkeypatch.delenv("EAOS_OIDC_REFRESH_KEY_PROVIDER", raising=False)
    monkeypatch.delenv("EAOS_OIDC_REFRESH_FERNET_KEY", raising=False)
    monkeypatch.delenv("EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS", raising=False)
    configure_oidc_refresh_store(
        store="memory", encrypt=None, reencrypt_on_read=None, key_provider=None
    )
    clear_oidc_states()
    clear_oidc_discovery_cache()
    clear_runtime_denylist()
    clear_jwks_cache()
    configure_jwt_settings(
        JwtSettings(
            secret="eaos-g70-secret",
            issuer="https://eaos.example/issuer",
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
        )
    )
    configure_oidc(None)
    yield
    clear_oidc_states()
    configure_oidc_refresh_store(store="memory", encrypt=None, reencrypt_on_read=None)


def test_reencrypt_default_off() -> None:
    assert refresh_reencrypt_on_read_enabled() is False
    client = TestClient(create_app())
    status = client.get("/v1/auth/oidc/status")
    assert status.json()["data"]["refresh_reencrypt_on_read"] is False


def test_get_rewrites_old_ciphertext_to_primary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EAOS_OIDC_REFRESH_ENCRYPT", "1")
    monkeypatch.setenv("EAOS_OIDC_REFRESH_FERNET_KEY", OLD_KEY)
    configure_oidc_refresh_store(store="memory", encrypt=None, reencrypt_on_read=None)
    put_oidc_session(
        "jti-rot",
        OidcSessionBinding(
            refresh_token="refresh-old-key",
            id_token="id-old-key",
            created_at=1.0,
        ),
    )
    old_cipher = _SESSIONS["jti-rot"].refresh_token
    assert old_cipher is not None and old_cipher.startswith("eaos1:")

    monkeypatch.setenv("EAOS_OIDC_REFRESH_FERNET_KEY", NEW_KEY)
    monkeypatch.setenv("EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS", OLD_KEY)
    monkeypatch.setenv("EAOS_OIDC_REFRESH_REENCRYPT_ON_READ", "1")
    configure_oidc_refresh_store(store="memory", encrypt=None, reencrypt_on_read=None)
    # restore sealed payload after configure clear
    _SESSIONS["jti-rot"] = OidcSessionBinding(
        refresh_token=old_cipher,
        id_token=None,
        created_at=1.0,
    )
    assert ciphertext_needs_primary_rotation(old_cipher) is True

    opened = get_oidc_session("jti-rot")
    assert opened is not None
    assert opened.refresh_token == "refresh-old-key"

    new_cipher = _SESSIONS["jti-rot"].refresh_token
    assert new_cipher is not None
    assert new_cipher != old_cipher
    assert ciphertext_needs_primary_rotation(new_cipher) is False

    client = TestClient(create_app())
    body = client.get("/v1/auth/oidc/status").json()["data"]
    assert body["refresh_reencrypt_on_read"] is True
    assert body["refresh_encrypt_key_count"] == 2


def test_reencrypt_off_keeps_old_ciphertext(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_OIDC_REFRESH_ENCRYPT", "1")
    monkeypatch.setenv("EAOS_OIDC_REFRESH_FERNET_KEY", OLD_KEY)
    configure_oidc_refresh_store(store="memory", encrypt=None, reencrypt_on_read=None)
    put_oidc_session(
        "jti-keep",
        OidcSessionBinding(
            refresh_token="refresh-keep",
            id_token=None,
            created_at=1.0,
        ),
    )
    old_cipher = _SESSIONS["jti-keep"].refresh_token

    monkeypatch.setenv("EAOS_OIDC_REFRESH_FERNET_KEY", NEW_KEY)
    monkeypatch.setenv("EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS", OLD_KEY)
    monkeypatch.delenv("EAOS_OIDC_REFRESH_REENCRYPT_ON_READ", raising=False)
    configure_oidc_refresh_store(store="memory", encrypt=None, reencrypt_on_read=None)
    _SESSIONS["jti-keep"] = OidcSessionBinding(
        refresh_token=old_cipher,
        id_token=None,
        created_at=1.0,
    )
    assert get_oidc_session("jti-keep").refresh_token == "refresh-keep"
    assert _SESSIONS["jti-keep"].refresh_token == old_cipher
