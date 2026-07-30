"""PHX-G78 tenant IdP federation priority SQL adapter contracts."""

from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

fastapi = pytest.importorskip("fastapi")

from api.gateway.auth_jwt import JwtSettings, clear_jwks_cache
from api.gateway.context import configure_jwt_settings
from api.gateway.tenant_idp_federation import (
    clear_tenant_idp_federation,
    configure_tenant_idp_federation,
    create_tenant_idp_binding,
    list_tenant_idp_bindings,
    preferred_active_issuer,
    set_tenant_idp_binding_priority,
)
from kernel.infrastructure.persistence import metadata

TENANT = uuid4()
ISS_A = "https://g78-sql-a.example/eaos"
ISS_B = "https://g78-sql-b.example/eaos"


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


@pytest.fixture(autouse=True)
def _reset() -> None:
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


def test_priority_persists_across_sql_store() -> None:
    engine = _engine()
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    configure_tenant_idp_federation(store="sql", session_factory=factory)
    clear_tenant_idp_federation()

    a = create_tenant_idp_binding(tenant_id=TENANT, issuer=ISS_A)
    b = create_tenant_idp_binding(tenant_id=TENANT, issuer=ISS_B)
    assert a.priority == 100
    set_tenant_idp_binding_priority(b.id, priority=3)
    rows = list_tenant_idp_bindings(tenant_id=TENANT)
    assert rows[0].issuer == ISS_B
    assert rows[0].priority == 3
    assert preferred_active_issuer(TENANT) == ISS_B
