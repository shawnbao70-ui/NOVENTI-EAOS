"""PHX-G18 API Gateway foundation contracts."""

from __future__ import annotations

from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import app
from eaos_sdk.catalog import load_release_manifest

SUBJECT = str(uuid4())
TENANT = str(uuid4())
CORR = str(uuid4())


def _headers(**extra: str) -> dict[str, str]:
    base = {
        "X-EAOS-Subject-Id": SUBJECT,
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": TENANT,
        "X-Correlation-Id": CORR,
    }
    base.update(extra)
    return base


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def test_health_and_release(client: TestClient) -> None:
    health = client.get("/v1/health")
    assert health.status_code == 200
    assert health.json()["data"]["status"] == "ok"
    release = client.get("/v1/release")
    assert release.status_code == 200
    manifest = load_release_manifest()
    assert release.json()["data"]["version"] == manifest["version"]
    assert release.json()["data"]["alembic_head"] == manifest["alembic_head"]


def test_adapters_list(client: TestClient) -> None:
    response = client.get("/v1/adapters")
    assert response.status_code == 200
    names = {item["name"] for item in response.json()["data"]}
    assert "identity" in names
    assert "marketplace" in names
    assert "auth" in names
    assert response.json()["meta"]["count"] == 14


def test_context_requires_trusted_headers(client: TestClient) -> None:
    missing = client.get("/v1/context")
    assert missing.status_code == 401
    ok = client.get("/v1/context", headers=_headers())
    assert ok.status_code == 200
    data = ok.json()["data"]
    assert data["subject_id"] == SUBJECT
    assert data["tenant_id"] == TENANT
    assert data["platform_scope"] is False
    assert data["correlation_id"] == CORR


def test_body_cannot_elevate_context(client: TestClient) -> None:
    response = client.post(
        "/v1/context/echo",
        headers=_headers(),
        json={
            "tenant_id": str(uuid4()),
            "subject_id": str(uuid4()),
            "platform_scope": True,
            "note": "probe",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "TERMINAL_CONTEXT_ELEVATION_DENIED"

    allowed = client.post(
        "/v1/context/echo",
        headers=_headers(),
        json={"note": "ok"},
    )
    assert allowed.status_code == 200
    assert allowed.json()["data"]["context"]["tenant_id"] == TENANT
    assert allowed.json()["data"]["context"]["platform_scope"] is False


def test_marketplace_pricing_http_unknown_listing(client: TestClient) -> None:
    listing_id = str(uuid4())
    response = client.post(
        f"/v1/marketplace/listings/{listing_id}/pricing",
        headers=_headers(),
        json={"price": "1.00"},
    )
    assert response.status_code in {403, 404}
    assert response.json()["detail"]["code"] in {
        "MARKETPLACE_NOT_FOUND",
        "PERMISSION_DENIED",
    }
