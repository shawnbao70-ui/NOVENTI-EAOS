"""PHX-G90 Declared EAOS Roles Catalog SQL Store contracts."""

from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from api.gateway.role_catalog import reset_role_catalog
from api.gateway.role_catalog_store import (
    clear_role_catalog_store,
    configure_role_catalog_store,
    list_declared_roles,
    role_catalog_store_kind,
    upsert_declared_role,
)
from kernel.infrastructure.persistence import create_session_factory, metadata
from kernel.permission.service import PermissionService

GOVERNOR = uuid4()
TENANT = uuid4()
ADMIN = uuid4()
CORR = str(uuid4())


class _AllowPrincipalEligibility:
    def is_eligible(self, *, subject_id, tenant_id) -> bool:  # type: ignore[no-untyped-def]
        return True


def _engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.begin() as connection:
        connection.exec_driver_sql("ATTACH DATABASE ':memory:' AS kernel")
        metadata.create_all(connection)
    return engine


def _platform_headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(GOVERNOR),
        "X-EAOS-Subject-Type": "human",
        "X-Correlation-Id": CORR,
    }


def _tenant_headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(ADMIN),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }


@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("EAOS_ROLE_CATALOG_STORE", "EAOS_ROLE_CATALOG", "EAOS_DATABASE_URL"):
        monkeypatch.delenv(name, raising=False)
    configure_role_catalog_store(store="memory")
    clear_role_catalog_store()
    reset_role_catalog()
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
    clear_role_catalog_store()
    configure_role_catalog_store(store="memory")
    reset_role_catalog()


def _client() -> TestClient:
    service = PermissionService(
        grant_administrators={ADMIN},
        decision_auditors={ADMIN},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    return TestClient(create_app(permission_service=service))


def test_default_store_is_memory() -> None:
    assert role_catalog_store_kind() == "memory"


def test_sql_store_fail_closed_without_database_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EAOS_ROLE_CATALOG_STORE", "sql")
    configure_role_catalog_store(store=None)
    with pytest.raises(RuntimeError, match="EAOS_DATABASE_URL"):
        list_declared_roles()

    client = _client()
    response = client.get("/v1/platform/roles", headers=_platform_headers())
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "GATEWAY_ROLE_CATALOG_UNAVAILABLE"


def test_sql_store_round_trip_via_sqlite_metadata() -> None:
    factory = create_session_factory(_engine())
    configure_role_catalog_store(store="sql", session_factory=factory)

    created, action = upsert_declared_role(name="operator")
    assert action == "created"
    assert created.name == "operator"
    listed = list_declared_roles(include_disabled=True)
    assert len(listed) == 1
    assert listed[0].name == "operator"


def test_platform_upsert_disable_and_tenant_aggregate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EAOS_ROLE_CATALOG", "viewer")
    reset_role_catalog()
    client = _client()

    created = client.post(
        "/v1/platform/roles",
        headers=_platform_headers(),
        json={"name": "operator"},
    )
    assert created.status_code == 201
    role_id = created.json()["data"]["id"]
    assert created.json()["data"]["action"] == "created"

    tenant = client.get("/v1/permission/roles", headers=_tenant_headers())
    assert tenant.status_code == 200
    names = {row["name"] for row in tenant.json()["roles"]}
    assert names == {"viewer", "operator"}
    assert any(
        row["name"] == "operator" and "catalog" in row["sources"]
        for row in tenant.json()["roles"]
    )

    disabled = client.post(
        f"/v1/platform/roles/{role_id}/disable",
        headers=_platform_headers(),
        json={},
    )
    assert disabled.status_code == 200
    assert disabled.json()["data"]["status"] == "disabled"

    after = client.get("/v1/permission/roles", headers=_tenant_headers())
    assert {row["name"] for row in after.json()["roles"]} == {"viewer"}


def test_platform_list_includes_disabled() -> None:
    client = _client()
    created = client.post(
        "/v1/platform/roles",
        headers=_platform_headers(),
        json={"name": "admin"},
    )
    role_id = created.json()["data"]["id"]
    client.post(
        f"/v1/platform/roles/{role_id}/disable",
        headers=_platform_headers(),
        json={},
    )
    listed = client.get("/v1/platform/roles", headers=_platform_headers())
    assert listed.status_code == 200
    assert listed.json()["meta"]["count"] == 1
    assert listed.json()["data"][0]["status"] == "disabled"
