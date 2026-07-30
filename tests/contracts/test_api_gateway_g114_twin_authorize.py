"""PHX-G114 Twin Authorize Fail-Closed Thin Probe contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
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


def test_terminal_exposes_twin_authorize_control() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminTwinAuthorize"' in html
    assert "Authorize from twin (expect 403)" in html
    assert "Twin authorize fail-closed 探针（G114" in html
    assert "Twin Terminal 运维面齐" in html
    assert "twinAuthorize" in js
    assert "adminAuthorizeFromTwin" in js
    start = js.index("async function adminAuthorizeFromTwin")
    end = js.index("async function adminPublishBrainInsight")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "twinAuthorize" in chunk
    assert "expected_fail_closed" in chunk
    assert "/brain/" not in chunk
    assert 'twinAuthorize: (id) => `/v1/twin/snapshots/${id}/authorize`' in js


def test_twin_authorize_fail_closed_probe_api() -> None:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=OPERATOR,
        resource_type="twin_snapshot",
        actions={"write", "read"},
    ).ok
    client = TestClient(
        create_app(
            permission_service=permission,
            twin_service=TwinService(permission),
        )
    )

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Authorize from twin" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminAuthorizeFromTwin" in script.text

    created = client.post(
        "/v1/twin/snapshots",
        headers=_headers(),
        json={
            "entity_ref": "plant:g114",
            "state": {"load": 1},
            "source_ref": "sensor:g114",
            "reason": "authorize-probe",
            "confidence": 0.9,
        },
    )
    assert created.status_code == 201
    snapshot_id = created.json()["data"]

    denied = client.post(
        f"/v1/twin/snapshots/{snapshot_id}/authorize",
        headers=_headers(),
    )
    assert denied.status_code == 403
    assert denied.json()["detail"]["code"] == "TWIN_EXECUTION_FORBIDDEN"
