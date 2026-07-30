"""PHX-G335 Brain execute / Twin authorize Permission-gated open (HTTP + OpenAPI)."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.common import AuthorizedResult
from eaos_platform.brain.service import BrainService
from eaos_platform.twin.service import TwinService
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.crm.customer_advisory import CustomerAdvisoryService

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


def _client(*, with_execute: bool = False, with_authorize: bool = False) -> TestClient:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    twin = TwinService(permission)
    brain = BrainService(permission, twin_reader=twin)
    twin_actions = {"write", "read"}
    brain_actions = {"publish", "read"}
    if with_authorize:
        twin_actions = twin_actions | {"authorize"}
    if with_execute:
        brain_actions = brain_actions | {"execute"}
    for resource_type, actions in (
        ("twin_snapshot", twin_actions),
        ("brain_insight", brain_actions),
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


def _seed(client: TestClient) -> tuple[str, str]:
    twin = client.post(
        "/v1/twin/snapshots",
        headers=_headers(),
        json={
            "entity_ref": "plant:g335-http",
            "state": {"load": 3},
            "source_ref": "sensor:g335",
            "reason": "http seed",
            "confidence": 0.75,
        },
    )
    assert twin.status_code == 201, twin.text
    snapshot_id = twin.json()["data"]
    insight = client.post(
        "/v1/brain/insights",
        headers=_headers(),
        json={
            "kind": "insight",
            "summary": "g335 seed",
            "confidence": 0.65,
            "source_ref": "model:g335",
            "reason": "http seed",
            "twin_ref": snapshot_id,
        },
    )
    assert insight.status_code == 201, insight.text
    return snapshot_id, insight.json()["data"]


def test_g335_http_deny_without_execute_authorize_grant() -> None:
    client = _client()
    snapshot_id, insight_id = _seed(client)
    denied_twin = client.post(
        f"/v1/twin/snapshots/{snapshot_id}/authorize",
        headers=_headers(),
    )
    assert denied_twin.status_code == 403
    assert denied_twin.json()["detail"]["code"] == "TWIN_EXECUTION_FORBIDDEN"
    denied_brain = client.post(
        f"/v1/brain/insights/{insight_id}/execute",
        headers=_headers(),
    )
    assert denied_brain.status_code == 403
    assert denied_brain.json()["detail"]["code"] == "BRAIN_EXECUTION_FORBIDDEN"


def test_g335_http_allow_with_execute_authorize_grant() -> None:
    client = _client(with_execute=True, with_authorize=True)
    snapshot_id, insight_id = _seed(client)
    allowed_twin = client.post(
        f"/v1/twin/snapshots/{snapshot_id}/authorize",
        headers=_headers(),
    )
    assert allowed_twin.status_code == 200, allowed_twin.text
    body_twin = allowed_twin.json()
    assert body_twin["data"]["authorized"] is True
    AuthorizedResult.model_validate(body_twin)

    allowed_brain = client.post(
        f"/v1/brain/insights/{insight_id}/execute",
        headers=_headers(),
    )
    assert allowed_brain.status_code == 200, allowed_brain.text
    body_brain = allowed_brain.json()
    assert body_brain["data"]["authorized"] is True
    AuthorizedResult.model_validate(body_brain)


def test_g335_status_permission_gated() -> None:
    client = _client()
    brain = client.get("/v1/brain/status")
    twin = client.get("/v1/twin/status")
    assert brain.status_code == 200
    assert twin.status_code == 200
    assert brain.json()["data"]["execute_execution"] == "permission_gated"
    assert twin.json()["data"]["authorize_execution"] == "permission_gated"


def test_g335_openapi_documents_200_and_403() -> None:
    doc = yaml.safe_load(
        (ROOT / "docs" / "api" / "brain.openapi.yaml").read_text(encoding="utf-8")
    )
    execute = doc["paths"]["/brain/insights/{insightId}/execute"]["post"]["responses"]
    authorize = doc["paths"]["/twin/snapshots/{snapshotId}/authorize"]["post"][
        "responses"
    ]
    for responses in (execute, authorize):
        assert "200" in responses
        assert "403" in responses
        assert "401" in responses
    assert (
        doc["components"]["schemas"]["BrainStatusData"]["properties"][
            "execute_execution"
        ]["const"]
        == "permission_gated"
    )
    assert (
        doc["components"]["schemas"]["TwinStatusData"]["properties"][
            "authorize_execution"
        ]["const"]
        == "permission_gated"
    )


def test_g335_z3_advisory_still_execution_authority_none() -> None:
    assert not hasattr(CustomerAdvisoryService, "request_execution")
    assert not hasattr(CustomerAdvisoryService, "authorize_from_twin")
    from noventi.crm import customer_advisory as advisory_mod

    text = Path(advisory_mod.__file__).read_text(encoding="utf-8")
    assert "execution_authority" in text
    assert '"none"' in text or "'none'" in text

