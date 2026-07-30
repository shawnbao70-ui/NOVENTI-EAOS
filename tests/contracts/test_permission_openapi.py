"""Normative PHX-K08 Permission OpenAPI and state-machine contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
OPENAPI_PATH = ROOT / "docs" / "api" / "permission.openapi.yaml"
STATE_MACHINE_PATH = (
    ROOT / "docs" / "architecture" / "PERMISSION_STATE_MACHINES.md"
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


def test_permission_openapi_is_versioned_and_complete() -> None:
    spec = _spec()
    assert spec["openapi"] == "3.1.0"
    assert spec["servers"] == [{"url": "/v1"}]
    assert spec["security"] == [{"bearerAuth": []}]
    assert {
        "/permission/roles/status",
        "/permission/roles",
        "/permission/policies",
        "/permission/policies/{policyId}/activation",
        "/permission/policies/{policyId}/deprecation",
        "/permission/grants",
        "/permission/grants/{grantId}/revocation",
        "/permission/grants/{grantId}/delegations",
        "/permission/evaluations",
        "/permission/decisions/{decisionId}/explanation",
        "/permission/principals/{subjectId}/effective-permissions",
    } <= set(spec["paths"])
    assert spec["info"]["version"].startswith("1.")


def test_permission_openapi_references_resolve() -> None:
    spec = _spec()
    for node in _walk(spec):
        ref = node.get("$ref")
        if ref is not None:
            _resolve_ref(spec, ref)


def test_permission_requests_cannot_assert_execution_context() -> None:
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


def test_permission_required_schemas_exist() -> None:
    spec = _spec()
    schemas = spec["components"]["schemas"]
    for name in (
        "PolicyRule",
        "CreatePolicyRequest",
        "GrantRequest",
        "DelegateRequest",
        "EvaluateRequest",
        "ErrorResponse",
        "UuidResult",
    ):
        assert name in schemas
    assert schemas["GrantRequest"]["properties"]["scope_level"]["$ref"].endswith(
        "ScopeLevel"
    )
    assert set(schemas["ScopeLevel"]["enum"]) == {
        "resource",
        "org_unit",
        "enterprise",
        "tenant",
    }


def test_permission_update_requests_require_expected_version() -> None:
    spec = _spec()
    versioned_reason = spec["components"]["schemas"]["VersionedReasonRequest"]
    assert "expected_version" in versioned_reason["required"]
    delegate = spec["components"]["schemas"]["DelegateRequest"]
    assert "expected_version" in delegate["required"]


def test_permission_operation_ids_are_unique() -> None:
    spec = _spec()
    operation_ids = [
        operation["operationId"]
        for path_item in spec["paths"].values()
        for method, operation in path_item.items()
        if method in {"get", "post", "put", "patch", "delete"}
    ]
    assert len(operation_ids) == len(set(operation_ids))


def test_permission_state_machines_cover_policy_grant_delegation_evaluate() -> None:
    document = STATE_MACHINE_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Policy",
        "## 2. Grant",
        "## 3. Delegation",
        "## 4. Evaluate Combining",
        "## 5. 并发",
    ):
        assert heading in document
    assert "PERMISSION_VERSION_CONFLICT" in document
    assert "deny overrides" in document
