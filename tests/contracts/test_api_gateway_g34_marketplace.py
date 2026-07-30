"""PHX-G34 Gateway Marketplace technical HTTP contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from eaos_platform.marketplace.service import MarketplaceService
from kernel.permission.service import PermissionService

ADMIN = uuid4()
ACTOR = uuid4()
TENANT = uuid4()
CORR = str(uuid4())


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _headers(subject_id=ACTOR, **extra: str) -> dict[str, str]:
    base = {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }
    base.update(extra)
    return base


@pytest.fixture()
def client() -> TestClient:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    admin_headers = _headers(subject_id=ADMIN)
    # Grants via service before app — use same permission instance
    from kernel.shared.context import ExecutionContext, SubjectType

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
    assert permission.grant(
        admin_ctx,
        principal_subject_id=ACTOR,
        resource_type="marketplace_acquisition",
        actions={"acquire", "read"},
    ).ok
    app = create_app(
        permission_service=permission,
        marketplace_service=MarketplaceService(permission),
    )
    _ = admin_headers
    return TestClient(app)


def test_marketplace_lifecycle_and_acquire(client: TestClient) -> None:
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

    assert (
        client.post(
            f"/v1/marketplace/listings/{listing_id}/signature",
            headers=_headers(),
            json={"signature_ref": "sig:ed25519:demo"},
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/v1/marketplace/listings/{listing_id}/submit",
            headers=_headers(),
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/v1/marketplace/listings/{listing_id}/review",
            headers=_headers(),
            json={"approve": True, "notes": "ok"},
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/v1/marketplace/listings/{listing_id}/publish",
            headers=_headers(),
        ).status_code
        == 200
    )

    got = client.get(
        f"/v1/marketplace/listings/{listing_id}",
        headers=_headers(),
    )
    assert got.status_code == 200
    assert got.json()["status"] == "published"
    assert got.json()["package_key"] == "noventi.demo.ops"

    acquired = client.post(
        f"/v1/marketplace/listings/{listing_id}/acquire",
        headers=_headers(),
    )
    assert acquired.status_code == 201
    assert acquired.json()["data"]

    revoked = client.post(
        f"/v1/marketplace/listings/{listing_id}/revoke",
        headers=_headers(),
    )
    assert revoked.status_code == 200
    assert revoked.json()["data"] is True


def test_marketplace_pricing_elevation_and_commercial(client: TestClient) -> None:
    response = client.post(
        f"/v1/marketplace/listings/{uuid4()}/pricing",
        headers=_headers(),
        json={"price": "1.00", "tenant_id": str(uuid4())},
    )
    assert response.status_code == 422
    locs = [tuple(err.get("loc", ())) for err in response.json()["detail"]]
    assert any("tenant_id" in loc for loc in locs)

    created = client.post(
        "/v1/marketplace/listings",
        headers=_headers(),
        json={
            "package_key": "noventi.commerce.http",
            "package_version": "1.0.0",
            "required_permissions": ["pkg.ops:read"],
            "data_scope": "tenant.ops",
        },
    )
    assert created.status_code == 201
    listing_id = created.json()["data"]
    priced = client.post(
        f"/v1/marketplace/listings/{listing_id}/pricing",
        headers=_headers(),
        json={"price": "1.00", "currency": "CNY"},
    )
    assert priced.status_code == 200
    assert priced.json()["data"] is True
    invoice = client.post(
        f"/v1/marketplace/listings/{listing_id}/invoices",
        headers=_headers(),
    )
    assert invoice.status_code == 201


def test_create_rejects_context_override(client: TestClient) -> None:
    response = client.post(
        "/v1/marketplace/listings",
        headers=_headers(),
        json={
            "package_key": "noventi.x",
            "package_version": "1.0.0",
            "required_permissions": ["a:b"],
            "data_scope": "tenant.x",
            "platform_scope": True,
        },
    )
    assert response.status_code == 422
    locs = [tuple(err.get("loc", ())) for err in response.json()["detail"]]
    assert any("platform_scope" in loc for loc in locs)
