"""PHX-G77 Tenant IdP Federation Policy Matrix API contracts."""

from __future__ import annotations

from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings, clear_jwks_cache
from api.gateway.context import configure_jwt_settings
from api.gateway.idp_registry import clear_idp_registry, configure_idp_registry
from api.gateway.tenant_idp_federation import (
    clear_tenant_idp_federation,
    configure_tenant_idp_federation,
)

GOVERNOR = uuid4()
TENANT_A = uuid4()
TENANT_B = uuid4()
CORR = str(uuid4())
ISS_BOUND = "https://g77-bound.example/eaos"
ISS_UNBOUND = "https://g77-unbound.example/eaos"


@pytest.fixture(autouse=True)
def _reset() -> None:
    configure_idp_registry(store="memory")
    clear_idp_registry()
    configure_tenant_idp_federation(store="memory")
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
    clear_idp_registry()
    configure_tenant_idp_federation(store="memory")
    configure_idp_registry(store="memory")


def _platform_headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(GOVERNOR),
        "X-EAOS-Subject-Type": "human",
        "X-Correlation-Id": CORR,
    }


def test_federation_matrix_lists_cross_tenant_cells() -> None:
    client = TestClient(create_app())
    assert (
        client.post(
            f"/v1/platform/idp/federation/tenants/{TENANT_A}/bindings",
            headers=_platform_headers(),
            json={"issuer": ISS_BOUND},
        ).status_code
        == 201
    )
    assert (
        client.post(
            f"/v1/platform/idp/federation/tenants/{TENANT_B}/bindings",
            headers=_platform_headers(),
            json={"issuer": ISS_BOUND},
        ).status_code
        == 201
    )

    matrix = client.get(
        "/v1/platform/idp/federation/matrix",
        headers=_platform_headers(),
    )
    assert matrix.status_code == 200
    body = matrix.json()
    cells = body["data"]["cells"]
    assert body["meta"]["tenant_count"] == 2
    assert body["meta"]["binding_count"] == 2
    assert {c["bound_tenant_id"] for c in cells if c["bound_tenant_id"]} == {
        str(TENANT_A),
        str(TENANT_B),
    }
    assert all(c["state"] == "active" for c in cells if c["binding_id"])
    for cell in cells:
        assert "tenant_id" not in cell


def test_federation_matrix_marks_unbound_registry_issuers() -> None:
    client = TestClient(create_app())
    created = client.post(
        "/v1/platform/idp/issuers",
        headers=_platform_headers(),
        json={"issuer": ISS_UNBOUND, "jwks_url": "https://g77-unbound.example/jwks"},
    )
    assert created.status_code == 201

    matrix = client.get(
        "/v1/platform/idp/federation/matrix",
        headers=_platform_headers(),
    )
    assert matrix.status_code == 200
    unbound = [
        c
        for c in matrix.json()["data"]["cells"]
        if c["state"] == "unbound" and c["issuer"].rstrip("/") == ISS_UNBOUND.rstrip("/")
    ]
    assert len(unbound) == 1
    assert unbound[0]["bound_tenant_id"] is None
    assert unbound[0]["binding_id"] is None
    assert unbound[0]["registry_status"] == "active"

    without = client.get(
        "/v1/platform/idp/federation/matrix?include_unbound_issuers=false",
        headers=_platform_headers(),
    )
    assert without.status_code == 200
    assert without.json()["meta"]["include_unbound_issuers"] is False
    assert all(c["state"] != "unbound" for c in without.json()["data"]["cells"])


def test_federation_matrix_platform_only() -> None:
    client = TestClient(create_app())
    missing = client.get("/v1/platform/idp/federation/matrix")
    assert missing.status_code == 401

    ok = client.get(
        "/v1/platform/idp/federation/matrix",
        headers=_platform_headers(),
    )
    assert ok.status_code == 200
    assert "cells" in ok.json()["data"]


def test_idp_status_federation_includes_matrix_summary() -> None:
    client = TestClient(create_app())
    client.post(
        f"/v1/platform/idp/federation/tenants/{TENANT_A}/bindings",
        headers=_platform_headers(),
        json={"issuer": ISS_BOUND},
    )
    status = client.get("/v1/auth/idp/status")
    assert status.status_code == 200
    federation = status.json()["data"]["federation"]
    assert "matrix" in federation
    assert federation["matrix"]["tenant_count"] >= 1
    assert federation["matrix"]["cell_count"] >= 1
    assert federation["binding_count"] >= 1
