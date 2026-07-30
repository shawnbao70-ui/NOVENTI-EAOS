"""Normative PHX-K09 Workflow OpenAPI and state-machine contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
OPENAPI_PATH = ROOT / "docs" / "api" / "workflow.openapi.yaml"
STATE_MACHINE_PATH = (
    ROOT / "docs" / "architecture" / "WORKFLOW_STATE_MACHINES.md"
)


def _spec() -> dict[str, Any]:
    loaded = yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _resolve_ref(spec: dict[str, Any], ref: str) -> Any:
    assert ref.startswith("#/")
    value: Any = spec
    for segment in ref[2:].split("/"):
        value = value[segment]
    return value


def _walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def test_workflow_openapi_is_versioned_and_complete() -> None:
    spec = _spec()
    assert spec["openapi"] == "3.1.0"
    assert spec["servers"] == [{"url": "/v1"}]
    assert spec["security"] == [{"bearerAuth": []}]
    assert {
        "/workflow/status",
        "/workflow/definitions",
        "/workflow/definitions/{definitionId}/deprecation",
        "/workflow/instances",
        "/workflow/instances/{instanceId}",
        "/workflow/instances/{instanceId}/signals",
        "/workflow/instances/{instanceId}/cancellation",
        "/workflow/instances/{instanceId}/compensation",
        "/workflow/instances/{instanceId}/tasks/{taskId}/approval",
        "/workflow/instances/{instanceId}/tasks/{taskId}/rejection",
        "/workflow/instances/{instanceId}/tasks/{taskId}/escalation",
        "/workflow/tasks",
    } <= set(spec["paths"])


def test_workflow_openapi_references_resolve() -> None:
    spec = _spec()
    for node in _walk(spec):
        ref = node.get("$ref")
        if ref is not None:
            _resolve_ref(spec, ref)


def test_workflow_requests_cannot_assert_execution_context() -> None:
    spec = _spec()
    headers = {
        parameter["name"].lower()
        for parameter in spec["components"]["parameters"].values()
        if parameter.get("in") == "header"
    }
    assert headers == {"x-correlation-id"}
    forbidden = {
        "execution_context",
        "tenant_id",
        "session_id",
        "platform_scope",
    }
    for name, schema in spec["components"]["schemas"].items():
        if name.endswith("Request"):
            assert forbidden.isdisjoint(schema.get("properties", {}))
            assert schema.get("additionalProperties") is False


def test_workflow_required_schemas_exist() -> None:
    spec = _spec()
    schemas = spec["components"]["schemas"]
    for name in (
        "CreateDefinitionRequest",
        "StartInstanceRequest",
        "SignalRequest",
        "TaskApprovalRequest",
        "TaskRejectionRequest",
        "TaskEscalationRequest",
        "CancelInstanceRequest",
        "CompensateInstanceRequest",
        "WorkflowInstance",
        "WorkflowTask",
        "ErrorResponse",
        "UuidResult",
    ):
        assert name in schemas
    start = schemas["StartInstanceRequest"]
    for field in (
        "approval_principal_id",
        "approval_action",
        "approval_resource_ref",
        "approval_plan_version",
        "approval_scope",
        "approval_expires_at",
        "approval_subject_id",
        "due_at",
    ):
        assert field in start["properties"]
    signal = schemas["SignalRequest"]
    assert "idempotency_key" in signal["required"]
    assert set(schemas["WorkflowStatus"]["enum"]) >= {
        "running",
        "pending_approval",
        "approved",
        "rejected",
        "cancelled",
        "completed",
        "compensating",
        "compensated",
    }


def test_workflow_update_requests_require_expected_version() -> None:
    spec = _spec()
    versioned_reason = spec["components"]["schemas"]["VersionedReasonRequest"]
    assert "expected_version" in versioned_reason["required"]
    signal = spec["components"]["schemas"]["SignalRequest"]
    assert "expected_version" in signal["required"]
    cancel = spec["components"]["schemas"]["CancelInstanceRequest"]
    assert "expected_version" in cancel["required"]
    compensate = spec["components"]["schemas"]["CompensateInstanceRequest"]
    assert "expected_version" in compensate["required"]
    approval = spec["components"]["schemas"]["TaskApprovalRequest"]
    assert "expected_instance_version" in approval["required"]
    assert "expected_task_version" in approval["required"]
    rejection = spec["components"]["schemas"]["TaskRejectionRequest"]
    assert "expected_instance_version" in rejection["required"]
    assert "expected_task_version" in rejection["required"]
    escalation = spec["components"]["schemas"]["TaskEscalationRequest"]
    assert "expected_instance_version" in escalation["required"]
    assert "expected_task_version" in escalation["required"]


def test_workflow_operation_ids_are_unique() -> None:
    spec = _spec()
    operation_ids = [
        operation["operationId"]
        for path_item in spec["paths"].values()
        for method, operation in path_item.items()
        if method in {"get", "post", "put", "patch", "delete"}
    ]
    assert len(operation_ids) == len(set(operation_ids))


def test_workflow_state_machines_cover_definition_instance_task_signal() -> None:
    document = STATE_MACHINE_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Definition",
        "## 2. Instance",
        "## 3. Task",
        "## 4. Signal Idempotency",
        "## 5. Dual Gate",
        "## 6. 并发",
    ):
        assert heading in document
    assert "WORKFLOW_VERSION_CONFLICT" in document
    assert "WORKFLOW_BUSINESS_KEY_CONFLICT" in document
    assert "WORKFLOW_APPROVAL_EXPIRED" in document
    assert "compensating" in document
    assert "dual" in document.lower() or "Dual Gate" in document
