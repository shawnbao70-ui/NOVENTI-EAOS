"""Normative Identity OpenAPI and state-machine contract checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
OPENAPI_PATH = ROOT / "docs" / "api" / "identity.openapi.yaml"
STATE_MACHINE_PATH = ROOT / "docs" / "architecture" / "IDENTITY_STATE_MACHINES.md"


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


def test_identity_openapi_is_versioned_and_has_required_surface() -> None:
    spec = _spec()
    assert spec["openapi"] == "3.1.0"
    assert spec["servers"] == [{"url": "/v1"}]
    assert spec["security"] == [{"bearerAuth": []}]
    required_paths = {
        "/identity/status",
        "/identity/subjects",
        "/identity/ai-employees",
        "/identity/ai-employees/{aiSubjectId}/profile",
        "/identity/ai-employees/{aiSubjectId}/assignments",
        "/identity/ai-employees/{aiSubjectId}/reassignments",
        "/identity/credentials",
        "/identity/sessions",
        "/identity/platform-governors",
    }
    assert required_paths <= set(spec["paths"])


def test_all_local_openapi_references_resolve() -> None:
    spec = _spec()
    for node in _walk(spec):
        ref = node.get("$ref")
        if ref is not None:
            _resolve_ref(spec, ref)


def test_client_cannot_assert_execution_context_security_fields() -> None:
    spec = _spec()
    headers = {
        parameter["name"].lower()
        for parameter in spec["components"]["parameters"].values()
        if parameter.get("in") == "header"
    }
    assert headers == {"x-correlation-id"}

    forbidden_properties = {
        "execution_context",
        "tenant_id",
        "session_id",
        "platform_scope",
    }
    request_schema_names = {
        name
        for name in spec["components"]["schemas"]
        if name.endswith("Request")
    }
    for name in request_schema_names:
        schema = spec["components"]["schemas"][name]
        assert forbidden_properties.isdisjoint(schema.get("properties", {}))


def test_operation_ids_are_unique_and_reassignment_is_coordinated() -> None:
    spec = _spec()
    operation_ids = [
        operation["operationId"]
        for path_item in spec["paths"].values()
        for method, operation in path_item.items()
        if method in {"get", "post", "put", "patch", "delete"}
    ]
    assert len(operation_ids) == len(set(operation_ids))
    reassignment = spec["paths"][
        "/identity/ai-employees/{aiSubjectId}/reassignments"
    ]["post"]
    assert reassignment["operationId"] == "coordinateAIReassignment"
    assert "Atomically ends old Organization memberships" in reassignment["description"]


def test_identity_state_machine_covers_all_persisted_lifecycles() -> None:
    document = STATE_MACHINE_PATH.read_text(encoding="utf-8")
    for heading in (
        "## Subject / AI Employee",
        "## Credential",
        "## Session",
        "## AI Assignment",
        "## Platform Identity Governor Grant",
        "## AI Employee Profile",
    ):
        assert heading in document
    assert "IDENTITY_AI_PROFILE_CONFLICT" in document
    assert "CTX_INVALID" in document
