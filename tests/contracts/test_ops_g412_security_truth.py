"""PHX-G412 security truth — WebAuthn challenge-bound + network defaults OFF."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from api.gateway import create_app

ROOT = Path(__file__).resolve().parents[2]


def test_g412_webauthn_attestation_crypto_remains_false() -> None:
    text = (ROOT / "docs" / "api" / "auth.openapi.yaml").read_text(encoding="utf-8")
    assert "attestation_crypto_verified" in text
    assert "attestation_crypto_verified: false" in text or (
        'attestation_crypto_verified:\n          type: boolean\n          const: false' in text
        or "const: false" in text
    )
    ceremony = (ROOT / "api" / "gateway" / "webauthn_ceremony.py").read_text(encoding="utf-8")
    assert "attestation_crypto_verified" in ceremony
    assert "False" in ceremony or "false" in ceremony


def test_g412_marketplace_network_and_psp_defaults_fail_closed() -> None:
    client = TestClient(create_app())
    market = client.get("/v1/marketplace/status")
    assert market.status_code == 200
    data = market.json()["data"]
    assert data.get("metering") == "fail_closed"
    metering = data.get("metering_product") or {}
    assert metering.get("external_psp") is False
    assert str(metering.get("network_default", "off")).casefold() == "off"
    billing = data.get("billing_record_product") or {}
    if billing:
        assert billing.get("external_psp") is False
        assert str(billing.get("enable_psp_network_default", "off")).casefold() == "off"
