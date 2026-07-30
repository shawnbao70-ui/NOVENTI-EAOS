"""PHX-G68 JWT tenant IdP federation enforcement contracts."""

from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

fastapi = pytest.importorskip("fastapi")

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings, clear_jwks_cache, mint_hs256_token
from api.gateway.context import configure_jwt_settings
from api.gateway.tenant_idp_federation import (
    clear_tenant_idp_federation,
    configure_tenant_idp_federation,
    create_tenant_idp_binding,
)

SUBJECT = uuid4()
TENANT = uuid4()
GOVERNOR = uuid4()
CORR = str(uuid4())
SECRET = "eaos-g68-secret"
EAOS_ISS = "https://eaos.example/issuer"
OIDC_ISS = "https://idp-g68.example"


@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EAOS_TENANT_IDP_FEDERATION", raising=False)
    monkeypatch.delenv("EAOS_TENANT_IDP_FEDERATION_STORE", raising=False)
    clear_tenant_idp_federation()
    configure_tenant_idp_federation(enforce=None, store="memory")
    clear_jwks_cache()
    configure_jwt_settings(
        JwtSettings(
            secret=SECRET,
            issuer=EAOS_ISS,
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
        )
    )
    yield
    clear_tenant_idp_federation()
    configure_tenant_idp_federation(enforce=None, store="memory")
    clear_jwks_cache()


def _token(**extra) -> str:  # type: ignore[no-untyped-def]
    claims = {
        "sub": str(SUBJECT),
        "eaos_tenant_id": str(TENANT),
        "eaos_subject_type": "human",
        "iss": EAOS_ISS,
        "aud": "eaos-api",
    }
    claims.update(extra)
    return mint_hs256_token(claims, secret=SECRET)


def test_federation_planes_include_jwt() -> None:
    client = TestClient(create_app())
    data = client.get("/v1/auth/idp/status").json()["data"]
    assert data["federation"]["planes"] == ["oidc", "jwt"]


def test_jwt_fail_closed_without_binding(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_TENANT_IDP_FEDERATION", "1")
    configure_tenant_idp_federation(enforce=None, store="memory")
    client = TestClient(create_app())
    denied = client.get(
        "/v1/context",
        headers={"Authorization": f"Bearer {_token(eaos_oidc_issuer=OIDC_ISS)}"},
    )
    assert denied.status_code == 403
    assert denied.json()["detail"]["code"] == "GATEWAY_TENANT_IDP_FEDERATION_DENIED"


def test_jwt_fail_closed_without_oidc_provenance(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_TENANT_IDP_FEDERATION", "1")
    configure_tenant_idp_federation(enforce=None, store="memory")
    create_tenant_idp_binding(tenant_id=TENANT, issuer=OIDC_ISS)
    client = TestClient(create_app())
    # EAOS iss alone is not federation provenance
    denied = client.get(
        "/v1/context",
        headers={"Authorization": f"Bearer {_token()}"},
    )
    assert denied.status_code == 403


def test_jwt_allows_when_bound(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_TENANT_IDP_FEDERATION", "1")
    configure_tenant_idp_federation(enforce=None, store="memory")
    create_tenant_idp_binding(tenant_id=TENANT, issuer=OIDC_ISS)
    client = TestClient(create_app())
    ok = client.get(
        "/v1/context",
        headers={"Authorization": f"Bearer {_token(eaos_oidc_issuer=OIDC_ISS)}"},
    )
    assert ok.status_code == 200
    assert ok.json()["data"]["tenant_id"] == str(TENANT)


def test_platform_plane_not_enforced(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_TENANT_IDP_FEDERATION", "1")
    configure_tenant_idp_federation(enforce=None, store="memory")
    client = TestClient(create_app())
    token = mint_hs256_token(
        {
            "sub": str(GOVERNOR),
            "eaos_platform_scope": True,
            "eaos_subject_type": "human",
            "iss": EAOS_ISS,
            "aud": "eaos-api",
        },
        secret=SECRET,
    )
    listed = client.get(
        f"/v1/platform/idp/federation/tenants/{TENANT}/bindings",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert listed.status_code == 200


def test_dev_headers_bypass_federation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_TENANT_IDP_FEDERATION", "1")
    configure_tenant_idp_federation(enforce=None, store="memory")
    client = TestClient(create_app())
    ok = client.get(
        "/v1/context",
        headers={
            "X-EAOS-Subject-Id": str(SUBJECT),
            "X-EAOS-Subject-Type": "human",
            "X-EAOS-Tenant-Id": str(TENANT),
            "X-Correlation-Id": CORR,
        },
    )
    assert ok.status_code == 200
