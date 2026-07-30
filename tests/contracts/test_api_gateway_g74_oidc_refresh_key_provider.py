"""PHX-G74 OIDC refresh Fernet key provider contracts."""

from __future__ import annotations

from pathlib import Path

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

fastapi = pytest.importorskip("fastapi")

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings, clear_jwks_cache, clear_runtime_denylist
from api.gateway.context import configure_jwt_settings
from api.gateway.oidc import clear_oidc_discovery_cache, clear_oidc_states, configure_oidc
from api.gateway.oidc_refresh_crypto import (
    refresh_key_provider,
    seal_token,
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
        "EAOS_OIDC_REFRESH_FERNET_KEY",
        "EAOS_OIDC_REFRESH_FERNET_KEY_FILE",
        "EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS",
        "EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS_FILE",
        "EAOS_OIDC_REFRESH_REENCRYPT_ON_READ",
    ):
        monkeypatch.delenv(name, raising=False)
    configure_oidc_refresh_store(
        store="memory", encrypt=None, reencrypt_on_read=None, key_provider=None
    )
    clear_oidc_states()
    clear_oidc_discovery_cache()
    clear_runtime_denylist()
    clear_jwks_cache()
    configure_jwt_settings(
        JwtSettings(
            secret="eaos-g74-secret",
            issuer="https://eaos.example/issuer",
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
        )
    )
    configure_oidc(None)
    yield
    clear_oidc_states()
    configure_oidc_refresh_store(
        store="memory", encrypt=None, reencrypt_on_read=None, key_provider=None
    )


def test_default_key_provider_is_env() -> None:
    assert refresh_key_provider() == "env"
    client = TestClient(create_app())
    status = client.get("/v1/auth/oidc/status")
    assert status.json()["data"]["refresh_encrypt_key_provider"] == "env"


def test_kms_provider_is_recognized(monkeypatch: pytest.MonkeyPatch) -> None:
    """G75 enables kms; G74 only asserted provider recognition remains non-env/file."""

    monkeypatch.setenv("EAOS_OIDC_REFRESH_KEY_PROVIDER", "kms")
    configure_oidc_refresh_store(
        store="memory", encrypt=None, reencrypt_on_read=None, key_provider=None
    )
    assert refresh_key_provider() == "kms"


def test_file_provider_round_trip(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    key_file = tmp_path / "primary.key"
    prev_file = tmp_path / "previous.keys"
    key_file.write_text(PRIMARY + "\n", encoding="utf-8")
    prev_file.write_text(f"# comment\n{PREVIOUS}\n", encoding="utf-8")

    monkeypatch.setenv("EAOS_OIDC_REFRESH_ENCRYPT", "1")
    monkeypatch.setenv("EAOS_OIDC_REFRESH_KEY_PROVIDER", "file")
    monkeypatch.setenv("EAOS_OIDC_REFRESH_FERNET_KEY_FILE", str(key_file))
    monkeypatch.setenv("EAOS_OIDC_REFRESH_FERNET_PREVIOUS_KEYS_FILE", str(prev_file))
    configure_oidc_refresh_store(
        store="memory", encrypt=None, reencrypt_on_read=None, key_provider=None
    )

    put_oidc_session(
        "jti-file",
        OidcSessionBinding(
            refresh_token="refresh-from-file",
            id_token=None,
            created_at=1.0,
        ),
    )
    assert get_oidc_session("jti-file").refresh_token == "refresh-from-file"

    client = TestClient(create_app())
    body = client.get("/v1/auth/oidc/status").json()["data"]
    assert body["refresh_encrypt_key_provider"] == "file"
    assert body["refresh_encrypt_key_count"] == 2
    assert PRIMARY not in str(body)
    assert PREVIOUS not in str(body)


def test_file_provider_fail_closed_without_key_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EAOS_OIDC_REFRESH_ENCRYPT", "1")
    monkeypatch.setenv("EAOS_OIDC_REFRESH_KEY_PROVIDER", "file")
    configure_oidc_refresh_store(
        store="memory", encrypt=None, reencrypt_on_read=None, key_provider=None
    )
    with pytest.raises(RuntimeError, match="FERNET_KEY_FILE"):
        seal_token("x")
