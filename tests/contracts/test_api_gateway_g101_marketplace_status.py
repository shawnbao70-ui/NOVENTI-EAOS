"""PHX-G101 Marketplace Status + Listing Thin Probe contracts."""

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


def test_terminal_exposes_marketplace_listing_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminMarketplaceStatus"' in html
    assert 'id="btnAdminListingCreate"' in html
    assert 'id="btnAdminListingGet"' in html
    assert 'id="listingId"' in html
    assert 'id="listingPackageKey"' in html
    assert "Marketplace 状态/listing 薄探针（G101" in html
    assert "支付清算仍 fail-closed" in html or "payment clearing" in html.casefold() or "G162" in html
    assert 'marketplaceStatus: "/v1/marketplace/status"' in js
    assert 'marketplaceListings: "/v1/marketplace/listings"' in js
    assert "adminCreateListing" in js
    assert "adminGetListing" in js
    start = js.index("async function adminCreateListing")
    end = js.index("async function adminGetListing")
    assert "tenant_id" not in js[start:end]
    assert "payment" not in js[start:end].lower()


def test_marketplace_status_and_listing_probe() -> None:
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
        actions={"create", "read"},
    ).ok
    client = TestClient(
        create_app(
            permission_service=permission,
            marketplace_service=MarketplaceService(permission),
        )
    )

    status = client.get("/v1/marketplace/status")
    assert status.status_code == 200
    data = status.json()["data"]
    assert data["writable"] is False
    assert data["payment_clearing"] in {"fail_closed", "internal_env_gated"}
    assert data.get("payment_clearing_product", {}).get("milestone") in {
        None,
        "PHX-G162",
    } or "payment_clearing_product" in data
    product = data.get("payment_clearing_product")
    if product is not None:
        assert product["milestone"] == "PHX-G162"
        assert product["external_psp"] is False
    assert data["external_arbitration"] == "fail_closed"
    assert data["metering"] == "fail_closed"
    assert "listing_lifecycle" in data["supported_surfaces"]

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Marketplace status" in page.text
    assert "Create listing" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminCreateListing" in script.text

    created = client.post(
        "/v1/marketplace/listings",
        headers=_headers(),
        json={
            "package_key": "noventi.demo.ops",
            "package_version": "1.0.0",
            "required_permissions": ["pkg.ops.brief:compose"],
            "declared_events": ["pkg.ops.brief.composed"],
            "data_scope": "tenant.ops",
        },
    )
    assert created.status_code == 201
    listing_id = created.json()["data"]
    fetched = client.get(
        f"/v1/marketplace/listings/{listing_id}",
        headers=_headers(),
    )
    assert fetched.status_code == 200
    assert fetched.json()["id"] == listing_id
    assert fetched.json()["package_key"] == "noventi.demo.ops"
