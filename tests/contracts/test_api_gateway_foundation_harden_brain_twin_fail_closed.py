"""Foundation harden — Brain execute / Twin authorize deny without execute grant."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

import pytest
import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.common import AuthorizedResult, OkResponse, UuidResult
from eaos_platform.brain.service import BrainService
from eaos_platform.twin.service import TwinService
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType

ROOT = Path(__file__).resolve().parents[2]
ADMIN = uuid4()
OPERATOR = uuid4()
TENANT = uuid4()


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(OPERATOR),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": str(uuid4()),
    }


def _admin_ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=ADMIN,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


@pytest.fixture()
def client() -> TestClient:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    twin = TwinService(permission)
    brain = BrainService(permission, twin_reader=twin)
    for resource_type, actions in (
        ("twin_snapshot", {"write", "read"}),
        ("brain_insight", {"publish", "read"}),
    ):
        assert permission.grant(
            _admin_ctx(),
            principal_subject_id=OPERATOR,
            resource_type=resource_type,
            actions=actions,
        ).ok
    return TestClient(
        create_app(
            permission_service=permission,
            twin_service=twin,
            brain_service=brain,
        )
    )


def _route(path: str, method: str):
    app = create_app()
    for route in app.routes:
        if getattr(route, "path", None) == path and method in getattr(
            route, "methods", set()
        ):
            return route
    raise AssertionError(f"missing route {method} {path}")


def test_permission_gated_routes_use_authorized_result_envelope() -> None:
    execute = _route("/v1/brain/insights/{insight_id}/execute", "POST")
    authorize = _route("/v1/twin/snapshots/{snapshot_id}/authorize", "POST")
    assert execute.response_model is AuthorizedResult
    assert authorize.response_model is AuthorizedResult
    assert execute.response_model not in {UuidResult, OkResponse}
    assert authorize.response_model not in {UuidResult, OkResponse}


def test_openapi_documents_200_and_403_for_execute_authorize() -> None:
    doc = yaml.safe_load(
        (ROOT / "docs" / "api" / "brain.openapi.yaml").read_text(encoding="utf-8")
    )
    execute = doc["paths"]["/brain/insights/{insightId}/execute"]["post"]["responses"]
    authorize = doc["paths"]["/twin/snapshots/{snapshotId}/authorize"]["post"][
        "responses"
    ]
    for responses in (execute, authorize):
        assert "403" in responses
        assert "200" in responses
        assert "401" in responses


def test_runtime_deny_without_execute_authorize_grant(client: TestClient) -> None:
    twin = client.post(
        "/v1/twin/snapshots",
        headers=_headers(),
        json={
            "entity_ref": "plant:harden",
            "state": {"load": 1},
            "source_ref": "sensor:harden",
            "reason": "harden",
            "confidence": 0.5,
        },
    )
    assert twin.status_code == 201, twin.text
    snapshot_id = twin.json()["data"]

    denied_twin = client.post(
        f"/v1/twin/snapshots/{snapshot_id}/authorize",
        headers=_headers(),
    )
    assert denied_twin.status_code == 403
    assert denied_twin.json()["detail"]["code"] == "TWIN_EXECUTION_FORBIDDEN"

    insight = client.post(
        "/v1/brain/insights",
        headers=_headers(),
        json={
            "kind": "insight",
            "summary": "advisory only",
            "confidence": 0.5,
            "source_ref": "model:harden",
            "reason": "harden",
        },
    )
    assert insight.status_code == 201, insight.text
    insight_id = insight.json()["data"]

    denied_brain = client.post(
        f"/v1/brain/insights/{insight_id}/execute",
        headers=_headers(),
    )
    assert denied_brain.status_code == 403
    assert denied_brain.json()["detail"]["code"] == "BRAIN_EXECUTION_FORBIDDEN"
