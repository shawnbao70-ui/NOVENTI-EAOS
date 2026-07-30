"""PHX-G28 Gateway Twin & Brain HTTP surface contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from eaos_platform.brain.service import BrainService
from eaos_platform.twin.service import TwinService
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType

ADMIN = uuid4()
OPERATOR = uuid4()
TENANT = uuid4()
CORR = str(uuid4())


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _headers(subject_id: UUID = OPERATOR, **extra: str) -> dict[str, str]:
    base = {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }
    base.update(extra)
    return base


def _admin_ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=ADMIN,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


@pytest.fixture()
def gateway() -> TestClient:
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


def test_twin_brain_require_trusted_headers(gateway: TestClient) -> None:
    assert gateway.get("/v1/twin/snapshots/" + str(uuid4())).status_code == 401
    assert gateway.get("/v1/brain/insights/" + str(uuid4())).status_code == 401


def test_twin_upsert_get_and_authorize_fail_closed(gateway: TestClient) -> None:
    created = gateway.post(
        "/v1/twin/snapshots",
        headers=_headers(),
        json={
            "entity_ref": "plant:1",
            "state": {"throughput": 10},
            "source_ref": "sensor:a",
            "reason": "sync",
            "confidence": 0.85,
        },
    )
    assert created.status_code == 201
    snapshot_id = created.json()["data"]

    fetched = gateway.get(
        f"/v1/twin/snapshots/{snapshot_id}",
        headers=_headers(),
    )
    assert fetched.status_code == 200
    assert fetched.json()["entity_ref"] == "plant:1"
    assert fetched.json()["confidence"] == 0.85
    assert fetched.json()["status"] == "active"

    denied = gateway.post(
        f"/v1/twin/snapshots/{snapshot_id}/authorize",
        headers=_headers(),
    )
    assert denied.status_code == 403
    assert denied.json()["detail"]["code"] == "TWIN_EXECUTION_FORBIDDEN"


def test_brain_publish_get_and_execute_fail_closed(gateway: TestClient) -> None:
    twin = gateway.post(
        "/v1/twin/snapshots",
        headers=_headers(),
        json={
            "entity_ref": "plant:2",
            "state": {"load": 3},
            "source_ref": "sensor:b",
            "reason": "baseline",
            "confidence": 0.7,
        },
    )
    twin_id = twin.json()["data"]

    published = gateway.post(
        "/v1/brain/insights",
        headers=_headers(),
        json={
            "kind": "recommendation",
            "summary": "Reduce load",
            "confidence": 0.6,
            "source_ref": "model:v1",
            "reason": "advisory",
            "twin_ref": twin_id,
            "knowledge_refs": ["kg:ops"],
        },
    )
    assert published.status_code == 201
    insight_id = published.json()["data"]

    fetched = gateway.get(
        f"/v1/brain/insights/{insight_id}",
        headers=_headers(),
    )
    assert fetched.status_code == 200
    body = fetched.json()
    assert body["kind"] == "recommendation"
    assert body["advisory"] is True
    assert body["twin_ref"] == twin_id

    denied = gateway.post(
        f"/v1/brain/insights/{insight_id}/execute",
        headers=_headers(),
    )
    assert denied.status_code == 403
    assert denied.json()["detail"]["code"] == "BRAIN_EXECUTION_FORBIDDEN"


def test_brain_non_advisory_rejected(gateway: TestClient) -> None:
    response = gateway.post(
        "/v1/brain/insights",
        headers=_headers(),
        json={
            "kind": "insight",
            "summary": "must stay advisory",
            "confidence": 0.5,
            "source_ref": "model:v1",
            "reason": "test",
            "advisory": False,
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "BRAIN_ADVISORY_REQUIRED"


def test_body_cannot_elevate_context(gateway: TestClient) -> None:
    response = gateway.post(
        "/v1/twin/snapshots",
        headers=_headers(),
        json={
            "entity_ref": "plant:x",
            "state": {},
            "source_ref": "sensor",
            "reason": "sync",
            "confidence": 0.5,
            "tenant_id": str(uuid4()),
            "platform_scope": True,
        },
    )
    assert response.status_code == 422
    locs = [tuple(err.get("loc", ())) for err in response.json()["detail"]]
    assert any("tenant_id" in loc for loc in locs)
