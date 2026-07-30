"""PHX-G141 Marketplace Foundation commercial Terminal thin probe contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from eaos_platform.marketplace.service import MarketplaceService
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType

ROOT = Path(__file__).resolve().parents[2]
ADMIN = uuid4()
ACTOR = uuid4()
TENANT = uuid4()
CORR = str(uuid4())


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


@pytest.fixture(autouse=True)
def _reset() -> None:
    configure_jwt_settings(
        JwtSettings(
            secret="",
            issuer=None,
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
        )
    )
    yield


def _headers(subject_id: UUID = ACTOR) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }


def test_terminal_exposes_marketplace_commercial_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminListingSetPricing"' in html
    assert 'id="btnAdminListingCreateInvoice"' in html
    assert 'id="btnAdminListingOpenDispute"' in html
    assert 'id="btnAdminListingResolveDispute"' in html
    assert 'id="btnAdminListingSetRevenueShare"' in html
    assert "Marketplace Foundation 商业薄探针（G141" in html
    assert (
        "≠ 支付清算" in html
        or "非支付清算" in html
        or "G162" in html
        or "payment clearing" in html.casefold()
        or "外部 PSP" in html
    )
    assert "adminSetListingPricing" in js
    assert "adminCreateListingInvoice" in js
    assert "adminOpenListingDispute" in js
    assert "adminResolveListingDispute" in js
    assert "adminSetListingRevenueShare" in js
    start = js.index("async function adminSetListingPricing")
    end = js.index("async function adminCreateWorkflowDefinition")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    # G162 opens named payment-clearing route; still no external PSP rail invent
    assert "external arbitration" in chunk.lower() or "payment clearing" in chunk.lower()
    assert "stripe" not in chunk.lower()
    assert "paypal" not in chunk.lower()


def test_marketplace_commercial_probe_api() -> None:
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
            "submit",
            "review",
            "publish",
            "revoke",
            "read",
            "price",
            "invoice",
            "dispute",
            "revenue_share",
        },
    ).ok
    client = TestClient(
        create_app(
            permission_service=permission,
            marketplace_service=MarketplaceService(permission),
        )
    )

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Set listing pricing" in page.text
    assert "Create listing invoice" in page.text

    created = client.post(
        "/v1/marketplace/listings",
        headers=_headers(),
        json={
            "package_key": "noventi.demo.commerce",
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
        json={"price": "12.50", "currency": "CNY"},
    )
    assert priced.status_code == 200
    assert priced.json()["data"] is True

    invoice = client.post(
        f"/v1/marketplace/listings/{listing_id}/invoices",
        headers=_headers(),
    )
    assert invoice.status_code == 201
    assert invoice.json()["data"]

    dispute = client.post(
        f"/v1/marketplace/listings/{listing_id}/disputes",
        headers=_headers(),
        json={"reason": "g141 delivery"},
    )
    assert dispute.status_code == 201
    dispute_id = dispute.json()["data"]

    resolved = client.post(
        f"/v1/marketplace/disputes/{dispute_id}/resolve",
        headers=_headers(),
        json={"resolution": "g141 resolved"},
    )
    assert resolved.status_code == 200
    assert resolved.json()["data"] is True

    share = client.post(
        f"/v1/marketplace/listings/{listing_id}/revenue-share",
        headers=_headers(),
        json={"platform_share_bps": 2000},
    )
    assert share.status_code == 200
    assert share.json()["data"] is True
