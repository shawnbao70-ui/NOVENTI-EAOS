"""PHX-G78 Tenant IdP Federation Issuer Priority API contracts."""

from __future__ import annotations

from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings, clear_jwks_cache
from api.gateway.context import configure_jwt_settings
from api.gateway.tenant_idp_federation import (
    assert_tenant_idp_binding,
    clear_tenant_idp_federation,
    configure_tenant_idp_federation,
    preferred_active_issuer,
)

GOVERNOR = uuid4()
TENANT = uuid4()
CORR = str(uuid4())
ISS_A = "https://g78-a.example/eaos"
ISS_B = "https://g78-b.example/eaos"


@pytest.fixture(autouse=True)
def _reset() -> None:
    configure_tenant_idp_federation(store="memory", enforce=True)
    clear_tenant_idp_federation()
    clear_jwks_cache()
    configure_jwt_settings(
        JwtSettings(
            secret="",
            issuer=None,
            audience=None,
            allow_dev_headers=True,
            require_jwt=False,
        )
    )
    yield
    clear_tenant_idp_federation()
    configure_tenant_idp_federation(store="memory", enforce=None)


def _platform_headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(GOVERNOR),
        "X-EAOS-Subject-Type": "human",
        "X-Correlation-Id": CORR,
    }


def test_set_binding_priority_updates_and_orders_list() -> None:
    client = TestClient(create_app())
    a = client.post(
        f"/v1/platform/idp/federation/tenants/{TENANT}/bindings",
        headers=_platform_headers(),
        json={"issuer": ISS_A},
    )
    b = client.post(
        f"/v1/platform/idp/federation/tenants/{TENANT}/bindings",
        headers=_platform_headers(),
        json={"issuer": ISS_B},
    )
    assert a.status_code == 201
    assert b.status_code == 201
    assert a.json()["data"]["priority"] == 100
    id_a = a.json()["data"]["id"]
    id_b = b.json()["data"]["id"]

    set_b = client.post(
        f"/v1/platform/idp/federation/bindings/{id_b}/priority",
        headers=_platform_headers(),
        json={"priority": 10},
    )
    assert set_b.status_code == 200
    assert set_b.json()["data"]["priority"] == 10

    listed = client.get(
        f"/v1/platform/idp/federation/tenants/{TENANT}/bindings",
        headers=_platform_headers(),
    )
    assert listed.status_code == 200
    issuers = [row["issuer"] for row in listed.json()["data"]]
    assert issuers[0] == ISS_B
    assert issuers[1] == ISS_A
    assert listed.json()["data"][0]["id"] == id_b


def test_priority_body_rejects_tenant_id_override() -> None:
    client = TestClient(create_app())
    created = client.post(
        f"/v1/platform/idp/federation/tenants/{TENANT}/bindings",
        headers=_platform_headers(),
        json={"issuer": ISS_A},
    )
    binding_id = created.json()["data"]["id"]
    elevated = client.post(
        f"/v1/platform/idp/federation/bindings/{binding_id}/priority",
        headers=_platform_headers(),
        json={"priority": 1, "tenant_id": str(uuid4())},
    )
    assert elevated.status_code == 422
    locs = [tuple(err.get("loc", ())) for err in elevated.json()["detail"]]
    assert any("tenant_id" in loc for loc in locs)


def test_priority_body_rejects_bool() -> None:
    client = TestClient(create_app())
    created = client.post(
        f"/v1/platform/idp/federation/tenants/{TENANT}/bindings",
        headers=_platform_headers(),
        json={"issuer": ISS_A},
    )
    binding_id = created.json()["data"]["id"]
    response = client.post(
        f"/v1/platform/idp/federation/bindings/{binding_id}/priority",
        headers=_platform_headers(),
        json={"priority": True},
    )
    assert response.status_code == 422


def test_matrix_cells_include_priority() -> None:
    client = TestClient(create_app())
    created = client.post(
        f"/v1/platform/idp/federation/tenants/{TENANT}/bindings",
        headers=_platform_headers(),
        json={"issuer": ISS_A},
    )
    binding_id = created.json()["data"]["id"]
    client.post(
        f"/v1/platform/idp/federation/bindings/{binding_id}/priority",
        headers=_platform_headers(),
        json={"priority": 5},
    )
    matrix = client.get(
        "/v1/platform/idp/federation/matrix",
        headers=_platform_headers(),
    )
    assert matrix.status_code == 200
    cells = [
        c
        for c in matrix.json()["data"]["cells"]
        if c["binding_id"] == binding_id
    ]
    assert len(cells) == 1
    assert cells[0]["priority"] == 5


def test_preferred_active_issuer_picks_lowest_priority() -> None:
    client = TestClient(create_app())
    a = client.post(
        f"/v1/platform/idp/federation/tenants/{TENANT}/bindings",
        headers=_platform_headers(),
        json={"issuer": ISS_A},
    )
    b = client.post(
        f"/v1/platform/idp/federation/tenants/{TENANT}/bindings",
        headers=_platform_headers(),
        json={"issuer": ISS_B},
    )
    client.post(
        f"/v1/platform/idp/federation/bindings/{b.json()['data']['id']}/priority",
        headers=_platform_headers(),
        json={"priority": 1},
    )
    client.post(
        f"/v1/platform/idp/federation/bindings/{a.json()['data']['id']}/priority",
        headers=_platform_headers(),
        json={"priority": 50},
    )
    assert preferred_active_issuer(TENANT) == ISS_B


def test_assert_tenant_idp_binding_unchanged_by_priority() -> None:
    client = TestClient(create_app())
    a = client.post(
        f"/v1/platform/idp/federation/tenants/{TENANT}/bindings",
        headers=_platform_headers(),
        json={"issuer": ISS_A},
    )
    b = client.post(
        f"/v1/platform/idp/federation/tenants/{TENANT}/bindings",
        headers=_platform_headers(),
        json={"issuer": ISS_B},
    )
    client.post(
        f"/v1/platform/idp/federation/bindings/{a.json()['data']['id']}/priority",
        headers=_platform_headers(),
        json={"priority": 90},
    )
    client.post(
        f"/v1/platform/idp/federation/bindings/{b.json()['data']['id']}/priority",
        headers=_platform_headers(),
        json={"priority": 1},
    )
    # Higher priority (worse preference) issuer still allowed when active.
    assert_tenant_idp_binding(tenant_id=TENANT, issuer=ISS_A)
    assert_tenant_idp_binding(tenant_id=TENANT, issuer=ISS_B)
