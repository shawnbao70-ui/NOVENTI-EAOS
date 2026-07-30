"""PHX-G248 OpenAPI WebAuthn verify denial honesty."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import yaml

from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
API = ROOT / "docs" / "api"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g248_docs_present() -> None:
    assert (
        ROOT / "docs" / "decisions" / "ADR-0267-openapi-webauthn-verify-denial-honesty.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G248_ACCEPTANCE.md").is_file()

def test_g248_verify_denial_named() -> None:
    auth = _load(API / "auth.openapi.yaml")
    assert str(auth["info"]["version"]).startswith("1.3.")
    schemas = auth["components"]["schemas"]
    detail = schemas["WebauthnVerifyDenialDetail"]
    assert detail.get("additionalProperties") is False
    assert set(detail["required"]) >= {"code", "message", "ceremony_step"}
    assert set(detail["properties"]["code"]["enum"]) >= {
        "GATEWAY_WEBAUTHN_CHALLENGE_INVALID",
        "GATEWAY_WEBAUTHN_ATTESTATION_INVALID",
    }
    assert detail["properties"]["ceremony_step"].get("const") == "register_verify"
    verify400 = auth["paths"]["/auth/webauthn/register/verify"]["post"]["responses"]["400"]
    ref = verify400["content"]["application/json"]["schema"]["$ref"]
    assert ref.endswith("/WebauthnVerifyDenialError")

def test_g248_baseline() -> None:
    assert sdk_version == "0.2.5"
    assert_current_baseline()
    ledger = (ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md").read_text(
        encoding="utf-8"
    )
    assert "DAL-U121" in ledger
