"""PHX-G89 OIDC MFA Enrollment URL Gate contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4
from urllib.parse import parse_qs, urlparse

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings, mint_hs256_token as mint_id_token
from api.gateway.context import configure_jwt_settings
from api.gateway.oidc import OidcSettings, clear_oidc_states, configure_oidc
from api.gateway.oidc_amr_acr import reset_oidc_amr_acr
from api.gateway.oidc_mfa_enrollment import reset_oidc_mfa_enrollment
from api.gateway.oidc_refresh_store import configure_oidc_refresh_store

SECRET = "eaos-g89-mfa-enrollment-secret"
TENANT = uuid4()
SUBJECT = uuid4()
JWT_SETTINGS = JwtSettings(
    secret=SECRET,
    issuer="https://eaos.example/issuer",
    audience="eaos-api",
    allow_dev_headers=True,
    require_jwt=False,
)
ROOT = Path(__file__).resolve().parents[2]


class _FakeTokenClient:
    def __init__(self, *, id_claims: dict) -> None:
        self._id_claims = dict(id_claims)

    def exchange_code(self, **kwargs):  # type: ignore[no-untyped-def]
        token = mint_id_token(self._id_claims, secret="idp-secret")
        return {
            "id_token": token,
            "token_type": "Bearer",
            "expires_in": 3600,
        }

    def refresh(self, **kwargs):  # type: ignore[no-untyped-def]
        token = mint_id_token(self._id_claims, secret="idp-secret")
        return {"id_token": token, "token_type": "Bearer", "expires_in": 3600}


def _oidc_settings() -> OidcSettings:
    return OidcSettings(
        issuer="https://idp.example",
        client_id="eaos-client",
        client_secret="client-secret",
        redirect_uri="http://127.0.0.1:8000/v1/auth/oidc/callback",
        authorization_endpoint="https://idp.example/authorize",
        token_endpoint="https://idp.example/token",
        scopes="openid",
        default_tenant_id=str(TENANT),
        enabled=True,
    )


@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "EAOS_OIDC_MFA_ENROLLMENT_URL",
        "EAOS_OIDC_REQUIRED_AMR",
        "EAOS_OIDC_REQUIRED_ACR",
    ):
        monkeypatch.delenv(name, raising=False)
    reset_oidc_mfa_enrollment()
    reset_oidc_amr_acr()
    clear_oidc_states()
    configure_oidc_refresh_store(store="memory")
    configure_jwt_settings(JWT_SETTINGS)
    configure_oidc(
        _oidc_settings(),
        token_client=_FakeTokenClient(
            id_claims={
                "sub": str(SUBJECT),
                "eaos_tenant_id": str(TENANT),
                "nonce": "placeholder",
            }
        ),
    )
    yield
    reset_oidc_mfa_enrollment()
    reset_oidc_amr_acr()
    clear_oidc_states()
    configure_oidc(
        OidcSettings(
            issuer=None,
            client_id=None,
            client_secret=None,
            redirect_uri=None,
            authorization_endpoint=None,
            token_endpoint=None,
            scopes="openid",
            default_tenant_id=None,
            enabled=False,
        )
    )


def test_enrollment_empty_is_off() -> None:
    client = TestClient(create_app())
    status = client.get("/v1/auth/oidc/status").json()["data"]
    assert status["mfa_enrollment_enabled"] is False
    assert status["mfa_enrollment_url"] is None
    denied = client.get("/v1/auth/oidc/mfa-enrollment", follow_redirects=False)
    assert denied.status_code == 503
    assert denied.json()["detail"]["code"] == "GATEWAY_OIDC_MFA_ENROLLMENT_UNCONFIGURED"


def test_enrollment_redirect(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "EAOS_OIDC_MFA_ENROLLMENT_URL",
        "https://idp.example/account/mfa",
    )
    reset_oidc_mfa_enrollment()
    client = TestClient(create_app())
    status = client.get("/v1/auth/oidc/status").json()["data"]
    assert status["mfa_enrollment_enabled"] is True
    assert status["mfa_enrollment_url"] == "https://idp.example/account/mfa"
    response = client.get("/v1/auth/oidc/mfa-enrollment", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "https://idp.example/account/mfa"


def test_amr_denial_includes_enrollment_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_OIDC_REQUIRED_AMR", "mfa")
    monkeypatch.setenv(
        "EAOS_OIDC_MFA_ENROLLMENT_URL",
        "https://idp.example/account/mfa",
    )
    reset_oidc_amr_acr()
    reset_oidc_mfa_enrollment()
    fake = _FakeTokenClient(
        id_claims={
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "nonce": "x",
            "amr": ["pwd"],
        }
    )
    configure_oidc(_oidc_settings(), token_client=fake)
    client = TestClient(create_app())
    login = client.get("/v1/auth/oidc/login", follow_redirects=False)
    query = parse_qs(urlparse(login.headers["location"]).query)
    fake._id_claims["nonce"] = query["nonce"][0]
    callback = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "c-g89", "state": query["state"][0]},
        headers={"Accept": "application/json"},
    )
    assert callback.status_code == 401
    detail = callback.json()["detail"]
    assert detail["code"] == "GATEWAY_OIDC_AMR_REQUIRED"
    assert detail["details"]["mfa_enrollment_url"] == "https://idp.example/account/mfa"


def test_invalid_enrollment_url_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_OIDC_MFA_ENROLLMENT_URL", "ftp://evil.example/mfa")
    reset_oidc_mfa_enrollment()
    client = TestClient(create_app())
    status = client.get("/v1/auth/oidc/status").json()["data"]
    assert status["mfa_enrollment_enabled"] is False
    denied = client.get("/v1/auth/oidc/mfa-enrollment", follow_redirects=False)
    assert denied.status_code == 503
    assert denied.json()["detail"]["code"] == "GATEWAY_OIDC_MFA_ENROLLMENT_INVALID"


def test_terminal_exposes_mfa_enrollment_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnOidcMfaEnrollment"' in html
    assert "/v1/auth/oidc/mfa-enrollment" in js
    assert "loadOidcMfaEnrollmentLink" in js
    assert "mfa_enrollment_enabled" in js
