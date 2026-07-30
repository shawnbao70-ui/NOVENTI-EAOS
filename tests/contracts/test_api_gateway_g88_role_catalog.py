"""PHX-G88 Opt-in EAOS Roles Catalog Gate contracts."""

from __future__ import annotations

from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.oidc_claim_role import configure_oidc_claim_role, reset_oidc_claim_role
from api.gateway.role_catalog import reset_role_catalog
from api.gateway.role_catalog_store import (
    clear_role_catalog_store,
    configure_role_catalog_store,
)
from kernel.permission.role_grant_map import (
    configure_permission_role_grant_map,
    reset_permission_role_grant_map,
)
from kernel.permission.service import PermissionService

ADMIN = uuid4()
TENANT = uuid4()
CORR = "corr-g88"


class _AllowPrincipalEligibility:
    def is_eligible(self, *, subject_id, tenant_id) -> bool:  # type: ignore[no-untyped-def]
        return True


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(ADMIN),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }


@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "EAOS_ROLE_CATALOG",
        "EAOS_ROLE_CATALOG_STORE",
        "EAOS_OIDC_ROLE_CLAIM",
        "EAOS_OIDC_ROLE_MAP",
        "EAOS_PERMISSION_ROLE_GRANT_MAP",
    ):
        monkeypatch.delenv(name, raising=False)
    configure_role_catalog_store(store="memory")
    clear_role_catalog_store()
    reset_role_catalog()
    reset_oidc_claim_role()
    reset_permission_role_grant_map()
    yield
    clear_role_catalog_store()
    configure_role_catalog_store(store="memory")
    reset_role_catalog()
    reset_oidc_claim_role()
    reset_permission_role_grant_map()


def _client() -> TestClient:
    service = PermissionService(
        grant_administrators={ADMIN},
        decision_auditors={ADMIN},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    return TestClient(create_app(permission_service=service))


def test_empty_catalog() -> None:
    client = _client()
    response = client.get("/v1/permission/roles", headers=_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["enabled"] is False
    assert body["roles"] == []


def test_catalog_requires_trusted_context() -> None:
    client = _client()
    response = client.get("/v1/permission/roles")
    assert response.status_code == 401


def test_aggregates_oidc_grant_and_declared(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EAOS_ROLE_CATALOG", "viewer,operator")
    monkeypatch.setenv("EAOS_OIDC_ROLE_CLAIM", "groups")
    monkeypatch.setenv("EAOS_OIDC_ROLE_MAP", "Engineering=operator,Admins=admin")
    reset_oidc_claim_role()
    configure_oidc_claim_role()
    configure_permission_role_grant_map(
        {
            "operator": frozenset({("document", "read")}),
            "admin": frozenset({("document", "read"), ("document", "write")}),
        }
    )
    client = _client()
    response = client.get("/v1/permission/roles", headers=_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["enabled"] is True
    by_name = {row["name"]: row for row in body["roles"]}
    assert set(by_name) == {"admin", "operator", "viewer"}
    assert by_name["viewer"]["sources"] == ["catalog"]
    assert "grants" not in by_name["viewer"]
    assert by_name["operator"]["sources"] == ["catalog", "oidc_map", "grant_map"]
    assert by_name["operator"]["grants"] == [
        {"resource_type": "document", "action": "read"}
    ]
    assert by_name["admin"]["sources"] == ["oidc_map", "grant_map"]
    assert by_name["admin"]["grants"] == [
        {"resource_type": "document", "action": "read"},
        {"resource_type": "document", "action": "write"},
    ]
