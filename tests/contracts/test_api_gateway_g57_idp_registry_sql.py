"""PHX-G57 IdP registry SQL adapter contracts."""

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
from api.gateway.idp_registry import (
    clear_idp_registry,
    configure_idp_registry,
    create_idp_issuer,
    disable_idp_issuer,
    list_idp_issuers,
    registry_status_view,
    registry_store_kind,
)
from kernel.infrastructure.persistence import create_session_factory, metadata

GOVERNOR = uuid4()
CORR = str(uuid4())
REG_ISS = "https://sql-registry-idp.example/eaos"


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
    monkeypatch.delenv("EAOS_IDP_REGISTRY_STORE", raising=False)
    monkeypatch.delenv("EAOS_DATABASE_URL", raising=False)
    configure_idp_registry(store="memory")
    clear_idp_registry()
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
    clear_idp_registry()
    configure_idp_registry(store="memory")
    clear_jwks_cache()


def test_default_store_is_memory() -> None:
    assert registry_store_kind() == "memory"
    assert registry_status_view()["store"] == "process_memory"


def test_sql_store_fail_closed_without_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_IDP_REGISTRY_STORE", "sql")
    configure_idp_registry(store=None)
    with pytest.raises(RuntimeError, match="EAOS_DATABASE_URL"):
        list_idp_issuers()

    client = TestClient(create_app())
    response = client.get("/v1/platform/idp/issuers", headers=_platform_headers())
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "GATEWAY_IDP_REGISTRY_UNAVAILABLE"

    status = client.get("/v1/auth/idp/status")
    assert status.status_code == 200
    assert status.json()["data"]["registry"]["store"] == "unavailable"


def test_sql_store_round_trip_via_sqlite_metadata() -> None:
    factory = create_session_factory(_engine())
    configure_idp_registry(store="sql", session_factory=factory)

    created = create_idp_issuer(
        issuer=REG_ISS,
        jwks_url="https://sql-registry-idp.example/jwks",
        jwks_json=None,
    )
    assert created.status == "active"
    assert registry_status_view()["store"] == "sql"

    listed = list_idp_issuers(include_disabled=True)
    assert len(listed) == 1
    assert listed[0].issuer == REG_ISS

    disabled = disable_idp_issuer(created.id)
    assert disabled.status == "disabled"
    assert list_idp_issuers(include_disabled=False) == []

    # Unique issuer: reactivate disabled row
    again = create_idp_issuer(
        issuer=REG_ISS,
        jwks_url="https://sql-registry-idp.example/jwks2",
        jwks_json=None,
    )
    assert again.id == created.id
    assert again.status == "active"
    assert again.jwks_url.endswith("/jwks2")
    assert again.version >= 2


def test_sql_store_http_create_list_disable() -> None:
    factory = create_session_factory(_engine())
    configure_idp_registry(store="sql", session_factory=factory)
    client = TestClient(create_app())

    created = client.post(
        "/v1/platform/idp/issuers",
        headers=_platform_headers(),
        json={
            "issuer": REG_ISS,
            "jwks_url": "https://sql-registry-idp.example/jwks",
        },
    )
    assert created.status_code == 201
    issuer_id = created.json()["data"]["id"]

    listed = client.get("/v1/platform/idp/issuers", headers=_platform_headers())
    assert listed.status_code == 200
    assert listed.json()["meta"]["count"] == 1

    status = client.get("/v1/auth/idp/status")
    assert status.status_code == 200
    assert status.json()["data"]["registry"]["store"] == "sql"

    disabled = client.post(
        f"/v1/platform/idp/issuers/{issuer_id}/disable",
        headers=_platform_headers(),
        json={},
    )
    assert disabled.status_code == 200
    assert disabled.json()["data"]["status"] == "disabled"


def test_invalid_store_env_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_IDP_REGISTRY_STORE", "redis")
    configure_idp_registry(store=None)
    with pytest.raises(RuntimeError, match="memory or sql"):
        registry_store_kind()
