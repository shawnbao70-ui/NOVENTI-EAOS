"""Foundation harden — Auth JWT/OIDC/IdP status closed response envelopes."""

from __future__ import annotations

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.auth import (
    IdpStatusEnvelope,
    JwtStatusEnvelope,
    OidcProvidersEnvelope,
    OidcStatusEnvelope,
)
from api.gateway.schemas.permission import (
    PermissionRoleCatalogResponse,
    RoleCatalogStatusEnvelope,
)
from api.gateway.schemas.webauthn import WebauthnRegisterOptionsResponse
from api.gateway.webauthn_ceremony import mint_registration_options
from kernel.shared.context import ExecutionContext, SubjectType
from uuid import uuid4


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


def test_jwt_status_matches_closed_envelope(client: TestClient) -> None:
    response = client.get("/v1/auth/jwt/status")
    assert response.status_code == 200
    envelope = JwtStatusEnvelope.model_validate(response.json())
    assert envelope.data.writable is False
    data = response.json()["data"]
    assert "secret" not in data
    assert "jtis" not in data
    assert "denylist" in data


def test_oidc_providers_matches_closed_envelope(client: TestClient) -> None:
    response = client.get("/v1/auth/oidc/providers")
    assert response.status_code == 200
    envelope = OidcProvidersEnvelope.model_validate(response.json())
    assert isinstance(envelope.data.providers, list)


def test_oidc_status_matches_closed_envelope(client: TestClient) -> None:
    response = client.get("/v1/auth/oidc/status")
    assert response.status_code == 200
    envelope = OidcStatusEnvelope.model_validate(response.json())
    data = response.json()["data"]
    assert "client_secret" not in data
    assert envelope.data.oidc_login_product.surface == "foundation_oidc_login_product"
    assert envelope.data.webauthn_product.surface == "foundation_mfa_webauthn_product"


def test_idp_status_matches_closed_envelope(client: TestClient) -> None:
    response = client.get("/v1/auth/idp/status")
    assert response.status_code == 200
    envelope = IdpStatusEnvelope.model_validate(response.json())
    assert envelope.data.writable is False
    assert envelope.data.config_source == "environment+registry"
    data = response.json()["data"]
    assert "secret" not in data["jwt"]
    assert "client_secret" not in data["oidc"]


def _tenant_headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(uuid4()),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(uuid4()),
        "X-Correlation-Id": str(uuid4()),
    }


def test_role_catalog_status_matches_closed_envelope(client: TestClient) -> None:
    response = client.get("/v1/permission/roles/status", headers=_tenant_headers())
    assert response.status_code == 200
    envelope = RoleCatalogStatusEnvelope.model_validate(response.json())
    assert envelope.data.catalog_store in {"process_memory", "sql"}
    assert envelope.data.role_grant_product.surface == "foundation_role_grant_product"


def test_permission_roles_catalog_matches_closed_response(client: TestClient) -> None:
    response = client.get("/v1/permission/roles", headers=_tenant_headers())
    assert response.status_code == 200
    catalog = PermissionRoleCatalogResponse.model_validate(response.json())
    assert isinstance(catalog.roles, list)
    assert "data" not in response.json()


def test_webauthn_options_emit_matches_closed_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_WEBAUTHN_REGISTRATION_ENABLED", "true")
    monkeypatch.setenv("EAOS_WEBAUTHN_RP_ID", "localhost")
    monkeypatch.setenv("EAOS_WEBAUTHN_ORIGIN", "http://localhost")
    from api.gateway import webauthn_ceremony as ceremony

    ceremony.clear_webauthn_challenges()
    ctx = ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=uuid4(),
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )
    payload = mint_registration_options(ctx, {})
    closed = WebauthnRegisterOptionsResponse.model_validate(payload)
    assert closed.ceremony_step == "register_options"
    assert closed.registration_minted is False
    assert closed.publicKey.timeout == 60000
