"""PHX-G67 tenant IdP federation SQL adapter contracts."""

from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings, clear_jwks_cache
from api.gateway.context import configure_jwt_settings
from api.gateway.tenant_idp_federation import (
    clear_tenant_idp_federation,
    configure_tenant_idp_federation,
    create_tenant_idp_binding,
    federation_status_view,
    federation_store_kind,
    list_tenant_idp_bindings,
    unbind_tenant_idp_binding,
)
from kernel.infrastructure.persistence import create_session_factory, metadata

GOVERNOR = uuid4()
TENANT = uuid4()
CORR = str(uuid4())
ISS = "https://sql-fed-idp.example/eaos"


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


@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EAOS_TENANT_IDP_FEDERATION_STORE", raising=False)
    monkeypatch.delenv("EAOS_DATABASE_URL", raising=False)
    configure_tenant_idp_federation(store="memory")
    clear_tenant_idp_federation()
    clear_jwks_cache()
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
    clear_tenant_idp_federation()
    configure_tenant_idp_federation(store="memory")
    clear_jwks_cache()


def test_default_federation_store_is_memory() -> None:
    assert federation_store_kind() == "memory"
    assert federation_status_view()["store"] == "process_memory"


def test_sql_store_fail_closed_without_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_TENANT_IDP_FEDERATION_STORE", "sql")
    configure_tenant_idp_federation(store=None)
    with pytest.raises(RuntimeError, match="EAOS_DATABASE_URL"):
        list_tenant_idp_bindings()

    client = TestClient(create_app())
    response = client.get(
        f"/v1/platform/idp/federation/tenants/{TENANT}/bindings",
        headers=_platform_headers(),
    )
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "GATEWAY_TENANT_IDP_FEDERATION_UNAVAILABLE"

    status = client.get("/v1/auth/idp/status")
    assert status.status_code == 200
    assert status.json()["data"]["federation"]["store"] == "unavailable"


def test_sql_store_round_trip_via_sqlite_metadata() -> None:
    factory = create_session_factory(_engine())
    configure_tenant_idp_federation(store="sql", session_factory=factory)

    created = create_tenant_idp_binding(tenant_id=TENANT, issuer=ISS + "/")
    assert created.status == "active"
    assert created.issuer == ISS
    assert federation_status_view()["store"] == "sql"

    listed = list_tenant_idp_bindings(tenant_id=TENANT, include_disabled=True)
    assert len(listed) == 1

    disabled = unbind_tenant_idp_binding(created.id)
    assert disabled.status == "disabled"
    assert list_tenant_idp_bindings(tenant_id=TENANT, include_disabled=False) == []

    again = create_tenant_idp_binding(tenant_id=TENANT, issuer=ISS)
    assert again.id == created.id
    assert again.status == "active"
    assert again.version >= 2

    client = TestClient(create_app())
    http = client.get(
        f"/v1/platform/idp/federation/tenants/{TENANT}/bindings",
        headers=_platform_headers(),
    )
    assert http.status_code == 200
    assert http.json()["meta"]["count"] == 1
