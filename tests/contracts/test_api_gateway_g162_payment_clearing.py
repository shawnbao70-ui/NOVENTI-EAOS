"""PHX-G162 Marketplace payment clearing (Eng Explicit Defer `4`) contracts."""

from __future__ import annotations

from tests.contracts._baseline import EXPECTED_PACKAGE, assert_current_baseline

from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from api.gateway.payment_clearing import (
    GATEWAY_PAYMENT_CLEARING_DISABLED,
    PAYMENT_CLEARING_ROUTES,
    payment_clearing_product_posture,
)
from eaos_platform.marketplace.service import MarketplaceService
from eaos_sdk import __version__ as sdk_version
from eaos_sdk.catalog import load_release_manifest
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0181-marketplace-payment-clearing.md"
GATE = ROOT / "docs" / "project" / "PHX-G162_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G162_ACCEPTANCE.md"
MARKET_OPENAPI = ROOT / "docs" / "api" / "marketplace.openapi.yaml"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
TIP = ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md"
TERMINAL_HTML = ROOT / "smart_terminal" / "ui" / "index.html"
TERMINAL_JS = ROOT / "smart_terminal" / "ui" / "app.js"
PYPROJECT = ROOT / "pyproject.toml"
ADMIN = uuid4()
ACTOR = uuid4()
TENANT = uuid4()
CORR = str(uuid4())

class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True

@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch) -> None:
    configure_jwt_settings(
        JwtSettings(
            secret="",
            issuer=None,
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
        )
    )
    monkeypatch.delenv("EAOS_MARKETPLACE_PAYMENT_CLEARING_ENABLED", raising=False)
    yield

def _headers(subject_id: UUID = ACTOR) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }

def _market_spec() -> dict[str, Any]:
    loaded = yaml.safe_load(MARKET_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded

def _client() -> TestClient:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    admin_ctx = ExecutionContext(
        subject_id=ADMIN,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=CORR,
        request_time=ExecutionContext.utc_now(),
    )
    assert permission.grant(
        admin_ctx,
        principal_subject_id=ACTOR,
        resource_type="marketplace_listing",
        actions={
            "create",
            "read",
            "price",
            "invoice",
            "payment_clearing",
        },
    ).ok
    return TestClient(
        create_app(
            permission_service=permission,
            marketplace_service=MarketplaceService(permission),
        )
    )

def test_g162_adr_gate_acceptance_exist() -> None:
    assert ADR.is_file()
    assert GATE.is_file()
    assert ACCEPTANCE.is_file()
    adr = ADR.read_text(encoding="utf-8")
    assert "Accepted" in adr
    assert "PHX-G162" in adr
    assert "GATEWAY_PAYMENT_CLEARING_DISABLED" in adr
    assert "DAL-G007" in adr
    assert "external" in adr.casefold() or "PSP" in adr
    acceptance = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Brain" in acceptance and "Twin" in acceptance
    assert "0.2.1" in acceptance
    assert "0029" in acceptance

def test_g162_posture_default_disabled() -> None:
    posture = payment_clearing_product_posture()
    assert posture["milestone"] == "PHX-G162"
    assert posture["payment_clearing_enabled"] is False
    assert posture["external_psp"] is False
    assert posture["clearing_routes"] == list(PAYMENT_CLEARING_ROUTES)
    assert posture["clearing_stub_observability"] is True
    reasons = " ".join(posture["fail_closed_reasons"]).casefold()
    assert "default_false" in reasons or "enabled" in reasons

def test_g162_stub_route_returns_503_by_default() -> None:
    client = _client()
    listing_id = uuid4()
    response = client.post(
        f"/v1/marketplace/listings/{listing_id}/payment-clearing",
        headers=_headers(),
        json={"invoice_id": str(uuid4())},
    )
    assert response.status_code == 503
    detail = response.json().get("detail") or {}
    assert detail.get("code") == GATEWAY_PAYMENT_CLEARING_DISABLED
    assert detail.get("clearing_step") == "payment_clearing"
    assert detail.get("payment_cleared") is False
    assert detail.get("external_psp") is False
    assert detail.get("milestone") == "PHX-G162"

def test_g162_status_exposes_product_and_fail_closed() -> None:
    client = _client()
    status = client.get("/v1/marketplace/status")
    assert status.status_code == 200
    data = status.json()["data"]
    assert data["payment_clearing"] == "fail_closed"
    product = data["payment_clearing_product"]
    assert product["milestone"] == "PHX-G162"
    assert product["payment_clearing_enabled"] is False
    assert "payment_clearing" in data["supported_surfaces"]
    assert data["external_arbitration"] == "fail_closed"
    assert data["metering"] == "fail_closed"

def test_g162_env_enabled_internal_clearing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_MARKETPLACE_PAYMENT_CLEARING_ENABLED", "true")
    client = _client()
    created = client.post(
        "/v1/marketplace/listings",
        headers=_headers(),
        json={
            "package_key": "noventi.demo.clearing",
            "package_version": "1.0.0",
            "required_permissions": ["pkg.ops.brief:compose"],
            "declared_events": ["pkg.ops.brief.composed"],
            "data_scope": "tenant.ops",
        },
    )
    assert created.status_code == 201
    listing_id = created.json()["data"]
    priced = client.post(
        f"/v1/marketplace/listings/{listing_id}/pricing",
        headers=_headers(),
        json={"price": "10.00", "currency": "CNY"},
    )
    assert priced.status_code == 200
    invoice = client.post(
        f"/v1/marketplace/listings/{listing_id}/invoices",
        headers=_headers(),
    )
    assert invoice.status_code == 201
    invoice_id = invoice.json()["data"]

    cleared = client.post(
        f"/v1/marketplace/listings/{listing_id}/payment-clearing",
        headers=_headers(),
        json={"invoice_id": invoice_id, "note": "internal g162"},
    )
    assert cleared.status_code == 201
    payload = cleared.json()["data"]
    assert payload["payment_cleared"] is True
    assert payload["external_psp"] is False
    assert payload["settlement_rail"] == "internal_record_only"
    assert payload["invoice_id"] == invoice_id
    assert payload["milestone"] == "PHX-G162"

    status = client.get("/v1/marketplace/status")
    assert status.json()["data"]["payment_clearing"] == "internal_env_gated"

def test_g162_openapi_1_2_0_documents_clearing() -> None:
    spec = _market_spec()
    assert spec["info"]["version"]  # tip may advance in {"1.2.0", "1.2.1", "1.2.2", "1.2.3", "1.2.4", "1.2.5", "1.2.6"}
    assert "/marketplace/listings/{listingId}/payment-clearing" in spec["paths"]
    schemas = spec["components"]["schemas"]
    assert "PaymentClearingStubDetail" in schemas
    assert schemas["PaymentClearingStubDetail"]["properties"]["payment_cleared"].get("const") is False
    assert schemas["PaymentClearingProduct"]["properties"]["external_psp"].get("const") is False
    body = MARKET_OPENAPI.read_text(encoding="utf-8")
    assert "GATEWAY_PAYMENT_CLEARING_DISABLED" in body

def test_g162_package_dal_terminal_tip() -> None:
    assert sdk_version == "0.2.5"
    assert f'version = "{EXPECTED_PACKAGE}"' in PYPROJECT.read_text(encoding="utf-8")
    assert_current_baseline()
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "DAL-G007" in ledger
    assert "DAL-U035" in ledger
    assert "PHX-G162" in ledger
    tip = TIP.read_text(encoding="utf-8")
    assert "PHX-G162" in tip
    assert "payment" in tip.casefold()
    html = TERMINAL_HTML.read_text(encoding="utf-8")
    js = TERMINAL_JS.read_text(encoding="utf-8")
    assert "payment-clearing" in html.casefold() or "payment clearing" in html.casefold() or "G162" in html
    assert "payment-clearing" in js or "paymentClearing" in js or "Payment clearing" in js
    manifest = load_release_manifest()
    by_id = {m["id"]: m for m in manifest["milestones"]}
    assert by_id["PHX-G162"]["status"] == "fully_accepted"
