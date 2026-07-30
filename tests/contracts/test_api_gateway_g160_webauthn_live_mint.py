"""PHX-G160 WebAuthn env-gated live mint contracts."""

from __future__ import annotations

from tests.contracts._baseline import EXPECTED_PACKAGE, assert_current_baseline

import base64
import json
import os
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from api.gateway.webauthn_ceremony import (
    GATEWAY_WEBAUTHN_REGISTRATION_DISABLED,
    GATEWAY_WEBAUTHN_RP_CONFIG_REQUIRED,
    WEBAUTHN_CEREMONY_ROUTES,
    clear_webauthn_challenges,
)
from api.gateway.webauthn_product import webauthn_product_posture
from eaos_sdk import __version__ as sdk_version
from kernel.identity.models import SubjectKind
from kernel.identity.service import IdentityService
from kernel.shared.context import ExecutionContext, SubjectType

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0183-webauthn-live-mint.md"
GATE = ROOT / "docs" / "project" / "PHX-G160_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G160_ACCEPTANCE.md"
AUTH_OPENAPI = ROOT / "docs" / "api" / "auth.openapi.yaml"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
TERMINAL_HTML = ROOT / "smart_terminal" / "ui" / "index.html"
TERMINAL_JS = ROOT / "smart_terminal" / "ui" / "app.js"
PYPROJECT = ROOT / "pyproject.toml"
MANIFEST = ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"

TENANT = uuid4()
CORR = str(uuid4())
RP_ID = "localhost"
ORIGIN = "http://localhost:8000"

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

@pytest.fixture(autouse=True)
def _reset_env_and_challenges() -> None:
    configure_jwt_settings(
        JwtSettings(
            secret="",
            issuer=None,
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
        )
    )
    keys = (
        "EAOS_WEBAUTHN_REGISTRATION_ENABLED",
        "EAOS_WEBAUTHN_RP_ID",
        "EAOS_WEBAUTHN_ORIGIN",
        "EAOS_WEBAUTHN_RP_NAME",
    )
    previous = {key: os.environ.get(key) for key in keys}
    for key in keys:
        os.environ.pop(key, None)
    clear_webauthn_challenges()
    yield
    clear_webauthn_challenges()
    for key, value in previous.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

def _headers(subject_id: UUID) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }

def _auth_spec() -> dict[str, Any]:
    loaded = yaml.safe_load(AUTH_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded

def _client_with_subject() -> tuple[TestClient, UUID]:
    identity = IdentityService()
    ctx = ExecutionContext(
        tenant_id=TENANT,
        subject_id=uuid4(),
        subject_type=SubjectType.SERVICE,
        correlation_id=CORR,
        request_time=ExecutionContext.utc_now(),
        platform_scope=False,
    )
    reg = identity.register_subject(
        ctx, subject_type=SubjectKind.HUMAN, display_name="WebAuthn User"
    )
    assert reg.ok and reg.data is not None
    return TestClient(create_app(identity_service=identity)), reg.data

def test_g160_adr_gate_acceptance_exist() -> None:
    assert ADR.is_file()
    assert GATE.is_file()
    assert ACCEPTANCE.is_file()
    adr = ADR.read_text(encoding="utf-8")
    assert "Accepted" in adr
    assert "PHX-G160" in adr
    assert "EAOS_WEBAUTHN_REGISTRATION_ENABLED" in adr
    assert "DAL-G008" in adr
    assert "attestation_crypto_verified" in adr.casefold() or "attestation crypto" in adr.casefold()
    gate = GATE.read_text(encoding="utf-8")
    assert "DAL-G008" in gate
    acceptance = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Brain" in acceptance and "Twin" in acceptance
    assert "G161" in acceptance or "Role→grant" in acceptance

def test_g160_default_posture_and_503() -> None:
    posture = webauthn_product_posture()
    assert posture["milestone"] == "PHX-G160"
    assert posture["webauthn_registration_enabled"] is False
    assert posture["registration_enabled"] is False
    assert posture["webauthn_live_mint_ready"] is False
    assert posture["registration_routes"] == list(WEBAUTHN_CEREMONY_ROUTES)
    assert posture["attestation_mode"] == "disabled"

    client = TestClient(create_app())
    for path, step in (
        ("/v1/auth/webauthn/register/options", "register_options"),
        ("/v1/auth/webauthn/register/verify", "register_verify"),
    ):
        response = client.post(path)
        assert response.status_code == 503
        detail = response.json().get("detail") or {}
        assert detail.get("code") == GATEWAY_WEBAUTHN_REGISTRATION_DISABLED
        assert detail.get("ceremony_step") == step
        assert detail.get("registration_minted") is False
        assert detail.get("attestation_crypto_verified") is False
        assert detail.get("milestone") == "PHX-G160"

def test_g160_enabled_without_rp_returns_config_required() -> None:
    os.environ["EAOS_WEBAUTHN_REGISTRATION_ENABLED"] = "true"
    posture = webauthn_product_posture()
    assert posture["webauthn_registration_enabled"] is True
    assert posture["webauthn_rp_configured"] is False
    assert posture["webauthn_live_mint_ready"] is False

    client = TestClient(create_app())
    response = client.post("/v1/auth/webauthn/register/options")
    assert response.status_code == 503
    detail = response.json().get("detail") or {}
    assert detail.get("code") == GATEWAY_WEBAUTHN_RP_CONFIG_REQUIRED
    assert detail.get("registration_minted") is False
    assert detail.get("next_action") == "configure_rp_id_and_origin"

def test_g160_live_mint_options_and_verify() -> None:
    os.environ["EAOS_WEBAUTHN_REGISTRATION_ENABLED"] = "true"
    os.environ["EAOS_WEBAUTHN_RP_ID"] = RP_ID
    os.environ["EAOS_WEBAUTHN_ORIGIN"] = ORIGIN
    posture = webauthn_product_posture()
    assert posture["webauthn_live_mint_ready"] is True
    assert posture["attestation_mode"] == "challenge_bound"
    assert posture["live_enroll_path"] == "webauthn_challenge_bound_mint_g160"

    client, subject_id = _client_with_subject()
    headers = _headers(subject_id)
    options = client.post(
        "/v1/auth/webauthn/register/options",
        headers=headers,
        json={"user_name": "alice", "user_display_name": "Alice"},
    )
    assert options.status_code == 200
    body = options.json()
    assert body["ceremony_step"] == "register_options"
    assert body["registration_minted"] is False
    assert body["attestation_crypto_verified"] is False
    assert body["attestation_mode"] == "challenge_bound"
    assert body["milestone"] == "PHX-G160"
    challenge = body["publicKey"]["challenge"]
    assert body["publicKey"]["rp"]["id"] == RP_ID

    client_data = {
        "type": "webauthn.create",
        "challenge": challenge,
        "origin": ORIGIN,
    }
    credential = {
        "id": "cred-g160-test",
        "rawId": "cred-g160-test",
        "type": "public-key",
        "response": {
            "clientDataJSON": _b64url(json.dumps(client_data).encode("utf-8")),
            "attestationObject": _b64url(b"fake-attestation-object-bytes"),
        },
    }
    verify = client.post(
        "/v1/auth/webauthn/register/verify",
        headers=headers,
        json={"credential": credential},
    )
    assert verify.status_code == 200
    minted = verify.json()
    assert minted["ceremony_step"] == "register_verify"
    assert minted["registration_minted"] is True
    assert minted["attestation_verified"] is True
    assert minted["attestation_crypto_verified"] is False
    assert minted["attestation_mode"] == "challenge_bound"
    assert minted["credential_kind"] == "webauthn"
    assert minted["milestone"] == "PHX-G160"
    UUID(minted["credential_id"])

def test_g160_openapi_1_3_6_documents_mint() -> None:
    spec = _auth_spec()
    assert spec["info"]["version"].startswith("1.3.")
    paths = set(spec["paths"])
    assert "/auth/webauthn/register" not in paths
    assert "/auth/webauthn/register/options" in paths
    assert "/auth/webauthn/register/verify" in paths
    options = spec["paths"]["/auth/webauthn/register/options"]["post"]
    verify = spec["paths"]["/auth/webauthn/register/verify"]["post"]
    assert "200" in options["responses"]
    assert "503" in options["responses"]
    assert "200" in verify["responses"]
    assert "503" in verify["responses"]
    assert options["operationId"] == "mintWebauthnRegisterOptions"
    assert verify["operationId"] == "mintWebauthnRegisterVerify"
    schemas = spec["components"]["schemas"]
    assert "WebauthnRegisterOptionsResponse" in schemas
    assert "WebauthnRegisterVerifyResponse" in schemas
    product = schemas["WebauthnProductPosture"]["properties"]
    assert "const" not in product["webauthn_registration_enabled"]
    assert "webauthn_live_mint_ready" in product
    body = AUTH_OPENAPI.read_text(encoding="utf-8")
    assert "DAL-G008" in body
    assert "PHX-G160" in body
    assert "attestation_crypto_verified" in body

def test_g160_inventory_fence_attestation_crypto() -> None:
    inventory = openapi_inventory_product_posture()
    fences = inventory["known_defer_fences"]
    assert "webauthn_attestation_crypto_verify" in fences
    assert "webauthn_live_credential_mint" not in fences

def test_g160_package_dal_terminal_manifest() -> None:
    assert sdk_version == "0.2.5"
    assert f'version = "{EXPECTED_PACKAGE}"' in PYPROJECT.read_text(encoding="utf-8")
    assert_current_baseline()
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "DAL-G008" in ledger
    assert "DAL-U037" in ledger
    assert "PHX-G160" in ledger
    assert "继续WebAuthn live mint" in ledger
    html = TERMINAL_HTML.read_text(encoding="utf-8")
    js = TERMINAL_JS.read_text(encoding="utf-8")
    assert "G160" in html or "live mint" in html.casefold()
    assert "webauthn_live_mint_ready" in js or "EAOS_WEBAUTHN_REGISTRATION_ENABLED" in js
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    by_id = {row["id"]: row for row in manifest["milestones"]}
    assert by_id["PHX-G160"]["status"] == "fully_accepted"

def test_g160_no_attestation_crypto_brain_twin_register_path_claimed() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (ADR, GATE, ACCEPTANCE)
    )
    folded = combined.casefold()
    assert "attestation" in folded and "crypto" in folded
    assert "brain" in folded and "execute" in folded
    assert "twin" in folded and "authorize" in folded
    assert "/auth/webauthn/register" in combined or "ABSENT" in combined
    assert "brain execute enabled" not in folded
    assert "twin authorize enabled" not in folded
    assert "attestation_crypto_verified=true" not in folded
    assert "attestation_crypto_verified=false" in folded or "crypto" in folded
