"""PHX-G470–G475 Batch N Identity/Auth residual contracts."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.production_auth import ProductionAuthError, validate_production_auth

ROOT = Path(__file__).resolve().parents[2]
AUTH = ROOT / "docs" / "api" / "auth.openapi.yaml"
PERMISSION = ROOT / "docs" / "api" / "permission.openapi.yaml"
TERMINAL = ROOT / "smart_terminal" / "ui" / "app.js"


def test_g470_oidc_jwt_residual_honesty() -> None:
    client = TestClient(create_app())
    oidc = client.get("/v1/auth/oidc/status").json()["data"]
    jwt = client.get("/v1/auth/jwt/status").json()["data"]
    assert oidc["secrets_exposed"] is False
    assert oidc["pkce_s256_required"] is True
    assert jwt["secrets_exposed"] is False
    assert jwt["production_auth_fail_closed"] is True


def test_g471_webauthn_attestation_remains_closed() -> None:
    data = TestClient(create_app()).get("/v1/auth/oidc/status").json()["data"]
    product = data["webauthn_product"]
    assert product["registration_default_off"] is True
    assert product["attestation_crypto_verified"] is False
    assert product["attestation_mode"] in {"disabled", "challenge_bound"}


def test_g472_role_grant_default_off_contract() -> None:
    spec = yaml.safe_load(PERMISSION.read_text(encoding="utf-8"))
    props = spec["components"]["schemas"]["RoleGrantProductPosture"]["properties"]
    assert props["auto_write_default_off"]["const"] is True


def test_g473_production_auth_still_fails_closed() -> None:
    with pytest.raises(ProductionAuthError):
        validate_production_auth(
            settings=JwtSettings(
                secret="",
                issuer=None,
                audience=None,
                allow_dev_headers=True,
                require_jwt=False,
            ),
            environ={"EAOS_ENV": "production"},
        )


def test_g474_terminal_and_openapi_auth_strip() -> None:
    js = TERMINAL.read_text(encoding="utf-8")
    assert "attestation_crypto_verified=" in js
    spec = yaml.safe_load(AUTH.read_text(encoding="utf-8"))
    oidc = spec["components"]["schemas"]["OidcStatusData"]["properties"]
    jwt = spec["components"]["schemas"]["JwtStatusData"]["properties"]
    webauthn = spec["components"]["schemas"]["WebauthnProductPosture"]["properties"]
    assert oidc["secrets_exposed"]["const"] is False
    assert oidc["pkce_s256_required"]["const"] is True
    assert jwt["production_auth_fail_closed"]["const"] is True
    assert webauthn["attestation_crypto_verified"]["const"] is False
