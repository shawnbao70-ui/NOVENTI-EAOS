"""PHX-G140 Terminal Ops echo + Workflow definition deprecation contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from kernel.permission.service import PermissionService
from kernel.workflow.service import WorkflowService

ROOT = Path(__file__).resolve().parents[2]
ACTOR = uuid4()
TENANT = uuid4()
CORR = str(uuid4())


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


def _headers(subject_id: UUID = ACTOR) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }


def test_terminal_exposes_ops_echo_and_workflow_deprecate_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminContextEcho"' in html
    assert 'id="btnAdminWorkflowDeprecateDefinition"' in html
    assert 'id="workflowDeprecateReason"' in html
    assert "Ops context echo elevation-reject 与 Workflow definition deprecation 薄探针（G140" in html
    assert "adminContextEchoElevationReject" in js
    assert "adminDeprecateWorkflowDefinition" in js
    assert "contextEcho" in js
    assert "workflowDefinitionDeprecation" in js
    start = js.index("async function adminContextEchoElevationReject")
    end = js.index("function parseOptionalJwksJson")
    chunk = js[start:end]
    assert "platform_scope" in chunk  # intentional elevation probe payload
    assert "expected_elevation_reject" in chunk
    deprecate_start = js.index("async function adminDeprecateWorkflowDefinition")
    deprecate_end = js.index("async function adminStartWorkflowInstance")
    deprecate_chunk = js[deprecate_start:deprecate_end]
    assert "tenant_id" not in deprecate_chunk
    assert "platform_scope" not in deprecate_chunk


def test_ops_echo_and_workflow_deprecate_probe_api() -> None:
    permission = PermissionService()
    workflow = WorkflowService(
        permission,
        definition_administrators={ACTOR},
    )
    client = TestClient(
        create_app(permission_service=permission, workflow_service=workflow)
    )

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Context echo (expect 400 elevation)" in page.text
    assert "Deprecate workflow definition" in page.text

    echo = client.post(
        "/v1/context/echo",
        headers=_headers(),
        json={
            "tenant_id": str(uuid4()),
            "platform_scope": True,
            "note": "g140",
        },
    )
    assert echo.status_code == 400
    assert echo.json()["detail"]["code"] == "TERMINAL_CONTEXT_ELEVATION_DENIED"

    created = client.post(
        "/v1/workflow/definitions",
        headers=_headers(),
        json={
            "name": f"Flow-{uuid4()}",
            "definition_document_ref": "docs/workflows/g140",
            "version": "1.0",
        },
    )
    assert created.status_code == 201
    definition_id = created.json()["id"]

    deprecated = client.post(
        f"/v1/workflow/definitions/{definition_id}/deprecation",
        headers=_headers(),
        json={"reason": "g140 retire", "expected_version": 1},
    )
    assert deprecated.status_code == 200
    assert deprecated.json().get("ok") is True
