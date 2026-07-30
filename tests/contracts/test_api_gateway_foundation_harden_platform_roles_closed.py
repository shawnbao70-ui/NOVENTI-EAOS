"""Foundation harden — Platform declared-roles closed response envelopes."""

from __future__ import annotations

from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.platform import (
    DeclaredRoleActionEnvelope,
    DeclaredRoleListEnvelope,
    FederationMatrixEnvelope,
    IdpIssuerListEnvelope,
    TenantIdpBindingListEnvelope,
)


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


def _platform_headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(uuid4()),
        "X-EAOS-Subject-Type": "human",
        "X-Correlation-Id": str(uuid4()),
    }


def test_platform_roles_list_matches_closed_envelope(client: TestClient) -> None:
    response = client.get("/v1/platform/roles", headers=_platform_headers())
    assert response.status_code == 200
    envelope = DeclaredRoleListEnvelope.model_validate(response.json())
    assert envelope.meta.count == len(envelope.data)


def test_platform_roles_upsert_matches_closed_envelope(client: TestClient) -> None:
    name = f"noventi.harden.{uuid4().hex[:8]}"
    response = client.post(
        "/v1/platform/roles",
        headers=_platform_headers(),
        json={"name": name},
    )
    assert response.status_code == 201
    envelope = DeclaredRoleActionEnvelope.model_validate(response.json())
    assert envelope.data.name == name
    assert envelope.data.action in {"created", "updated", "reactivated", "unchanged"}


def test_platform_idp_issuers_list_matches_closed_envelope(client: TestClient) -> None:
    response = client.get("/v1/platform/idp/issuers", headers=_platform_headers())
    assert response.status_code == 200
    envelope = IdpIssuerListEnvelope.model_validate(response.json())
    assert envelope.meta.count == len(envelope.data)
    for item in envelope.data:
        assert "jwks_json" not in item.model_dump()


def test_platform_idp_federation_matrix_matches_closed_envelope(
    client: TestClient,
) -> None:
    response = client.get(
        "/v1/platform/idp/federation/matrix",
        headers=_platform_headers(),
    )
    assert response.status_code == 200
    envelope = FederationMatrixEnvelope.model_validate(response.json())
    assert envelope.meta.cell_count == len(envelope.data.cells)


def test_platform_idp_federation_bindings_list_matches_closed_envelope(
    client: TestClient,
) -> None:
    tenant_id = uuid4()
    response = client.get(
        f"/v1/platform/idp/federation/tenants/{tenant_id}/bindings",
        headers=_platform_headers(),
    )
    assert response.status_code == 200
    envelope = TenantIdpBindingListEnvelope.model_validate(response.json())
    assert envelope.meta.count == len(envelope.data)
