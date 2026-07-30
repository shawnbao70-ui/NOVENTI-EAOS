"""PHX-G116 Brain Execute Fail-Closed Thin Probe contracts."""

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


def test_terminal_exposes_brain_execute_control() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminBrainExecute"' in html
    assert "Execute brain insight (expect 403)" in html
    assert "Brain execute fail-closed 探针（G116" in html
    assert "Brain Terminal 运维面齐" in html
    assert "brainExecute" in js
    assert "adminExecuteBrainInsight" in js
    start = js.index("async function adminExecuteBrainInsight")
    end = js.index("async function adminCreateAiRun")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "brainExecute" in chunk
    assert "expected_fail_closed" in chunk
    assert 'brainExecute: (id) => `/v1/brain/insights/${id}/execute`' in js


def test_brain_execute_fail_closed_probe_api() -> None:
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

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Execute brain insight" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminExecuteBrainInsight" in script.text

    twin_created = client.post(
        "/v1/twin/snapshots",
        headers=_headers(),
        json={
            "entity_ref": "plant:g116",
            "state": {"load": 4},
            "source_ref": "sensor:g116",
            "reason": "baseline",
            "confidence": 0.8,
        },
    )
    assert twin_created.status_code == 201
    twin_id = twin_created.json()["data"]

    published = client.post(
        "/v1/brain/insights",
        headers=_headers(),
        json={
            "kind": "recommendation",
            "summary": "Hold steady",
            "confidence": 0.55,
            "source_ref": "model:g116",
            "reason": "advisory",
            "twin_ref": twin_id,
        },
    )
    assert published.status_code == 201
    insight_id = published.json()["data"]

    denied = client.post(
        f"/v1/brain/insights/{insight_id}/execute",
        headers=_headers(),
    )
    assert denied.status_code == 403
    assert denied.json()["detail"]["code"] == "BRAIN_EXECUTION_FORBIDDEN"
