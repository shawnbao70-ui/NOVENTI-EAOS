"""PHX-G46 JWT denylist / revocation contracts."""

from __future__ import annotations

import json
import time
from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import (
    JwtSettings,
    clear_denylist_cache,
    mint_hs256_token,
)
from api.gateway.context import configure_jwt_settings

SECRET = "eaos-denylist-test-secret"
SUBJECT = uuid4()
TENANT = uuid4()
ISS = "https://issuer.example/eaos"
REVOKED_JTI = "revoked-jti-001"
ACTIVE_JTI = "active-jti-002"


@pytest.fixture(autouse=True)
def _reset() -> None:
    clear_denylist_cache()
    configure_jwt_settings(
        JwtSettings(
            secret=SECRET,
            issuer=ISS,
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
            denylist_json=json.dumps(
                [
                    {"jti": REVOKED_JTI, "iss": ISS},
                    {"jti": "expired-entry", "exp": 1},
                    ACTIVE_JTI.replace("active", "string-form-unused"),
                ]
            ),
        )
    )
    yield
    clear_denylist_cache()
    configure_jwt_settings(
        JwtSettings(
            secret="",
            issuer=None,
            audience=None,
            allow_dev_headers=True,
            require_jwt=False,
        )
    )


def _token(*, jti: str, iss: str = ISS) -> str:
    return mint_hs256_token(
        {
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "eaos_subject_type": "human",
            "iss": iss,
            "aud": "eaos-api",
            "exp": int(time.time()) + 3600,
            "jti": jti,
        },
        secret=SECRET,
    )


def test_revoked_jti_rejected() -> None:
    client = TestClient(create_app())
    response = client.get(
        "/v1/context",
        headers={"Authorization": f"Bearer {_token(jti=REVOKED_JTI)}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "GATEWAY_JWT_REVOKED"


def test_active_jti_accepted() -> None:
    client = TestClient(create_app())
    response = client.get(
        "/v1/context",
        headers={"Authorization": f"Bearer {_token(jti=ACTIVE_JTI)}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["tenant_id"] == str(TENANT)


def test_denylist_iss_scope_not_matched() -> None:
    # Same jti but different iss — entry requires ISS
    other_iss = "https://other.example"
    configure_jwt_settings(
        JwtSettings(
            secret=SECRET,
            issuer=None,
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
            denylist_json=json.dumps([{"jti": REVOKED_JTI, "iss": ISS}]),
        )
    )
    client = TestClient(create_app())
    response = client.get(
        "/v1/context",
        headers={"Authorization": f"Bearer {_token(jti=REVOKED_JTI, iss=other_iss)}"},
    )
    assert response.status_code == 200


def test_denylist_url_fetch(monkeypatch: pytest.MonkeyPatch) -> None:
    url = "https://denylist.example/revoked.json"

    class _Resp:
        def read(self) -> bytes:
            return json.dumps([{"jti": "url-revoked"}]).encode("utf-8")

        def __enter__(self) -> _Resp:
            return self

        def __exit__(self, *args: object) -> bool:
            return False

    monkeypatch.setattr(
        "api.gateway.auth_jwt.urllib.request.urlopen",
        lambda request_url, timeout=5: _Resp(),
    )
    clear_denylist_cache()
    configure_jwt_settings(
        JwtSettings(
            secret=SECRET,
            issuer=ISS,
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
            denylist_url=url,
        )
    )
    client = TestClient(create_app())
    denied = client.get(
        "/v1/context",
        headers={"Authorization": f"Bearer {_token(jti='url-revoked')}"},
    )
    assert denied.status_code == 401
    assert denied.json()["detail"]["code"] == "GATEWAY_JWT_REVOKED"
    ok = client.get(
        "/v1/context",
        headers={"Authorization": f"Bearer {_token(jti='still-good')}"},
    )
    assert ok.status_code == 200
