"""PHX-G115 Brain Status / Insight Thin Probe contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from eaos_platform.brain.service import BrainService
from eaos_platform.twin.service import TwinService
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType

ROOT = Path(__file__).resolve().parents[2]
ADMIN = uuid4()
OPERATOR = uuid4()
TENANT = uuid4()
CORR = str(uuid4())


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


@pytest.fixture(autouse=True)
def _reset() -> None:
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


def _headers(subject_id: UUID = OPERATOR) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }


def _admin_ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=ADMIN,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=CORR,
        request_time=ExecutionContext.utc_now(),
    )


def test_terminal_exposes_brain_probe_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminBrainStatus"' in html
    assert 'id="btnAdminBrainPublishInsight"' in html
    assert 'id="btnAdminBrainGetInsight"' in html
    assert 'id="brainInsightId"' in html
    assert 'id="brainKind"' in html
    assert "Brain 状态/insight 薄探针（G115" in html
    assert 'brainStatus: "/v1/brain/status"' in js
    assert 'brainInsights: "/v1/brain/insights"' in js
    assert "adminPublishBrainInsight" in js
    assert "adminGetBrainInsight" in js
    start = js.index("async function adminPublishBrainInsight")
    end = js.index("async function adminExecuteBrainInsight")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "/execute" not in chunk


def test_brain_status_and_probe_api() -> None:
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
    client = TestClient(
        create_app(
            permission_service=permission,
            twin_service=twin,
            brain_service=brain,
        )
    )

    status = client.get("/v1/brain/status")
    assert status.status_code == 200
    data = status.json()["data"]
    assert data["writable"] is False
    assert data["execute_execution"] == "permission_gated"
    assert data["advisory_required"] is True
    assert "insight_publish" in data["supported_surfaces"]
    assert "insight_get" in data["supported_surfaces"]
    assert "request_execution" in data["supported_surfaces"]

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Brain status" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminPublishBrainInsight" in script.text

    twin_created = client.post(
        "/v1/twin/snapshots",
        headers=_headers(),
        json={
            "entity_ref": "plant:g115",
            "state": {"load": 2},
            "source_ref": "sensor:g115",
            "reason": "baseline",
            "confidence": 0.7,
        },
    )
    assert twin_created.status_code == 201
    twin_id = twin_created.json()["data"]

    published = client.post(
        "/v1/brain/insights",
        headers=_headers(),
        json={
            "kind": "recommendation",
            "summary": "Reduce load",
            "confidence": 0.6,
            "source_ref": "model:g115",
            "reason": "advisory",
            "twin_ref": twin_id,
        },
    )
    assert published.status_code == 201
    insight_id = published.json()["data"]

    fetched = client.get(
        f"/v1/brain/insights/{insight_id}",
        headers=_headers(),
    )
    assert fetched.status_code == 200
    body = fetched.json()
    assert body["kind"] == "recommendation"
    assert body["advisory"] is True
    assert body["twin_ref"] == twin_id
