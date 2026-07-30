"""PHX-G65 OIDC refresh Fernet key rotation contracts."""

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
    open_token,
    refresh_encrypt_key_count,
    seal_token,
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
BAD_KEY = "not-a-valid-fernet-key!!"


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
            secret="eaos-g65-secret",
            issuer="https://eaos.example/issuer",
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
        )
    )
    configure_oidc(None)
    yield
    clear_oidc_states()
    configure_oidc_refresh_store(store="memory", encrypt=None)


def test_key_count_zero_when_encrypt_off() -> None:
    assert refresh_encrypt_key_count() == 0
    client = TestClient(create_app())
    status = client.get("/v1/auth/oidc/status")
    assert status.json()["data"]["refresh_encrypt_key_count"] == 0


def test_previous_keys_decrypt_old_ciphertext(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_OIDC_REFRESH_ENCRYPT", "1")
    monkeypatch.setenv("EAOS_OIDC_REFRESH_FERNET_KEY", OLD_KEY)
    configure_oidc_refresh_store(store="memory", encrypt=None)
    put_oidc_session(
        "jti-old",
        OidcSessionBinding(
            refresh_token="refresh-old",
            id_token="id-old",
            created_at=1.0,
        ),
    )
    cipher = _SESSIONS["jti-old"].refresh_token
    assert cipher is not None and cipher.startswith("eaos1:")

    monkeypatch.setenv("EAOS_OIDC_REFRESH_FERNET_KEY", NEW_KEY)
    monkeypatch.setenv("EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS", OLD_KEY)
    configure_oidc_refresh_store(store="memory", encrypt=None)
    # restore sealed payload after clear from configure
    _SESSIONS["jti-old"] = OidcSessionBinding(
        refresh_token=cipher,
        id_token=None,
        created_at=1.0,
    )
    assert refresh_encrypt_key_count() == 2
    assert get_oidc_session("jti-old").refresh_token == "refresh-old"

    sealed_new = seal_token("refresh-new")
    assert sealed_new is not None
    assert open_token(sealed_new) == "refresh-new"
    # new ciphertext must not open with old key alone
    monkeypatch.setenv("EAOS_OIDC_REFRESH_FERNET_KEY", OLD_KEY)
    monkeypatch.delenv("EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS", raising=False)
    from cryptography.fernet import InvalidToken

    with pytest.raises(InvalidToken):
        open_token(sealed_new)


def test_invalid_previous_key_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_OIDC_REFRESH_ENCRYPT", "1")
    monkeypatch.setenv("EAOS_OIDC_REFRESH_FERNET_KEY", NEW_KEY)
    monkeypatch.setenv("EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS", BAD_KEY)
    configure_oidc_refresh_store(store="memory", encrypt=None)
    with pytest.raises(RuntimeError, match="valid Fernet"):
        seal_token("x")


def test_status_exposes_key_count_not_material(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_OIDC_REFRESH_ENCRYPT", "1")
    monkeypatch.setenv("EAOS_OIDC_REFRESH_FERNET_KEY", NEW_KEY)
    monkeypatch.setenv("EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS", OLD_KEY)
    configure_oidc_refresh_store(store="memory", encrypt=None)
    client = TestClient(create_app())
    body = client.get("/v1/auth/oidc/status").json()["data"]
    assert body["refresh_encrypt"] == "fernet"
    assert body["refresh_encrypt_key_count"] == 2
    raw = str(body)
    assert NEW_KEY not in raw
    assert OLD_KEY not in raw
