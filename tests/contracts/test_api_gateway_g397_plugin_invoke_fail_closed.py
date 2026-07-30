"""PHX-G397 Plugin invoke fail-closed honesty contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.terminal import TerminalStatusEnvelope
from kernel.permission.service import PermissionService
from kernel.workflow.service import WorkflowService
from smart_terminal.service import SmartTerminalService

ROOT = Path(__file__).resolve().parents[2]
TERMINAL_OPENAPI = ROOT / "docs" / "api" / "terminal.openapi.yaml"


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _load_openapi() -> dict[str, Any]:
    loaded = yaml.safe_load(TERMINAL_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_g397_terminal_status_invoke_fail_closed_flags() -> None:
    response = TestClient(create_app()).get("/v1/terminal/status")
    assert response.status_code == 200, response.text
    TerminalStatusEnvelope.model_validate(response.json())
    data = response.json()["data"]
    assert data["extension_invoke_mode"] == "sandboxed"
    assert data["extension_invoke_executed"] is False
    assert data["invoke_fail_closed_without_grant"] is True


def test_g397_invoke_unauthenticated_fail_closed() -> None:
    client = TestClient(create_app())
    response = client.post(
        f"/v1/terminal/extensions/{uuid4()}/actions",
        json={"action": "demo.ping", "surface": "ops.workbench"},
    )
    assert response.status_code == 401


def test_g397_invoke_without_grant_fail_closed() -> None:
    permission = PermissionService(principal_eligibility=_AllowAll())
    workflow = WorkflowService(permission)
    terminal = SmartTerminalService(permission, workflow)
    client = TestClient(
        create_app(
            permission_service=permission,
            workflow_service=workflow,
            terminal_service=terminal,
        )
    )
    stranger = uuid4()
    tenant = uuid4()
    response = client.post(
        f"/v1/terminal/extensions/{uuid4()}/actions",
        headers={
            "X-EAOS-Subject-Id": str(stranger),
            "X-EAOS-Subject-Type": "human",
            "X-EAOS-Tenant-Id": str(tenant),
            "X-Correlation-Id": f"corr-g397-{uuid4()}",
        },
        json={"action": "demo.ping", "surface": "ops.workbench"},
    )
    assert response.status_code in {403, 404}
    detail = response.json().get("detail") or {}
    if isinstance(detail, dict) and "code" in detail:
        assert detail["code"] in {
            "PERMISSION_DENIED",
            "PERMISSION_PRINCIPAL_INELIGIBLE",
            "COMMON_NOT_FOUND",
            "TERMINAL_EXTENSION_NOT_FOUND",
        }


def test_g397_openapi_documents_invoke_flags() -> None:
    props = _load_openapi()["components"]["schemas"]["TerminalStatusData"]["properties"]
    assert props["extension_invoke_mode"]["const"] == "sandboxed"
    assert props["extension_invoke_executed"]["const"] is False
    assert props["invoke_fail_closed_without_grant"]["const"] is True
