"""PHX-G113 Twin Status / Snapshot Thin Probe contracts."""

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


def test_terminal_exposes_twin_probe_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminTwinStatus"' in html
    assert 'id="btnAdminTwinUpsertSnapshot"' in html
    assert 'id="btnAdminTwinGetSnapshot"' in html
    assert 'id="twinSnapshotId"' in html
    assert 'id="twinEntityRef"' in html
    assert "Twin 状态/snapshot 薄探针（G113" in html
    assert 'twinStatus: "/v1/twin/status"' in js
    assert 'twinSnapshots: "/v1/twin/snapshots"' in js
    assert "adminUpsertTwinSnapshot" in js
    assert "adminGetTwinSnapshot" in js
    start = js.index("async function adminUpsertTwinSnapshot")
    end = js.index("async function adminAuthorizeFromTwin")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "/authorize" not in chunk
    assert "/brain/" not in chunk


def test_twin_status_and_probe_api() -> None:
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

    status = client.get("/v1/twin/status")
    assert status.status_code == 200
    data = status.json()["data"]
    assert data["writable"] is False
    assert data["authorize_execution"] == "permission_gated"
    assert "snapshot_upsert" in data["supported_surfaces"]
    assert "snapshot_get" in data["supported_surfaces"]
    assert "authorize_from_twin" in data["supported_surfaces"]

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Twin status" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminUpsertTwinSnapshot" in script.text

    created = client.post(
        "/v1/twin/snapshots",
        headers=_headers(),
        json={
            "entity_ref": "plant:g113",
            "state": {"throughput": 10},
            "source_ref": "sensor:g113",
            "reason": "probe",
            "confidence": 0.85,
        },
    )
    assert created.status_code == 201
    snapshot_id = created.json()["data"]

    fetched = client.get(
        f"/v1/twin/snapshots/{snapshot_id}",
        headers=_headers(),
    )
    assert fetched.status_code == 200
    assert fetched.json()["entity_ref"] == "plant:g113"
    assert fetched.json()["confidence"] == 0.85
