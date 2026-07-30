"""Foundation harden — Package surfaces / resolve closed response DTOs."""

from __future__ import annotations

from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.package import PackageSurfacesEnvelope, ResolvedActionResponse


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(uuid4()),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(uuid4()),
        "X-Correlation-Id": str(uuid4()),
    }


def test_package_surfaces_list_closed_when_authorized() -> None:
    client = TestClient(create_app())
    response = client.get("/v1/packages/surfaces", headers=_headers())
    if response.status_code == 200:
        envelope = PackageSurfacesEnvelope.model_validate(response.json())
        assert isinstance(envelope.data, list)
        return
    assert response.status_code in {403, 503}


def test_resolved_action_response_schema() -> None:
    payload = {
        "package_key": "noventi.sample.ops",
        "manifest_version": "1.0.0",
        "action_key": "ops.brief.compose",
        "resource_type": "pkg.ops.brief",
        "permission_action": "compose",
        "high_impact": False,
        "surface_key": "ops",
        "installation_id": str(uuid4()),
        "source": "package_manifest",
    }
    closed = ResolvedActionResponse.model_validate(payload)
    assert closed.source == "package_manifest"
    assert closed.high_impact is False
