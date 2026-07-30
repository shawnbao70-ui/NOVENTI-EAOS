"""PHX-G103 Marketplace Acquire Technical Thin Probe contracts."""

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


def test_terminal_exposes_acquire_control() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminListingAcquire"' in html
    assert "Acquire listing" in html
    assert "Marketplace acquire 技术薄探针（G103" in html
    assert "非外部 PSP" in html
    assert "marketplaceListingAcquire" in js
    assert "adminAcquireListing" in js
    start = js.index("async function adminAcquireListing")
    end = js.index("async function adminRevokeListing")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "payment" not in chunk.lower()
    assert "clearing" not in chunk.lower()


def test_gateway_serves_acquire_ui_and_api() -> None:
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
        },
    ).ok
    assert permission.grant(
        admin_ctx,
        principal_subject_id=ACTOR,
        resource_type="marketplace_acquisition",
        actions={"acquire", "read"},
    ).ok
    client = TestClient(
        create_app(
            permission_service=permission,
            marketplace_service=MarketplaceService(permission),
        )
    )
    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Acquire listing" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminAcquireListing" in script.text

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
            json={"signature_ref": "sig:g103"},
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
            json={"approve": True, "notes": "g103"},
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

    acquired = client.post(
        f"/v1/marketplace/listings/{listing_id}/acquire",
        headers=_headers(),
    )
    assert acquired.status_code == 201
    assert acquired.json()["data"]
