"""Normative PHX-K07 Organization OpenAPI and state-machine contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
OPENAPI_PATH = ROOT / "docs" / "api" / "organization.openapi.yaml"
STATE_MACHINE_PATH = (
    ROOT / "docs" / "architecture" / "ORGANIZATION_STATE_MACHINES.md"
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


def test_organization_openapi_is_versioned_and_complete() -> None:
    spec = _spec()
    assert spec["openapi"] == "3.1.0"
    assert spec["servers"] == [{"url": "/v1"}]
    assert spec["security"] == [{"bearerAuth": []}]
    assert {
        "/organization/status",
        "/platform/tenants",
        "/tenants/{tenantId}",
        "/platform/tenants/{tenantId}/suspension",
        "/enterprises",
        "/enterprises/{enterpriseId}",
        "/enterprises/{enterpriseId}/suspension",
        "/organization-units",
        "/organization-units/tree",
        "/organization-units/{unitId}/status",
        "/memberships",
        "/memberships/{membershipId}",
        "/memberships/{membershipId}/unit",
        "/memberships/{membershipId}/suspension",
    } <= set(spec["paths"])


def test_organization_openapi_references_resolve() -> None:
    spec = _spec()
    for node in _walk(spec):
        ref = node.get("$ref")
        if ref is not None:
            _resolve_ref(spec, ref)


def test_organization_requests_cannot_assert_execution_context() -> None:
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


def test_organization_update_requests_require_expected_version() -> None:
    spec = _spec()
    versioned_reason = spec["components"]["schemas"]["VersionedReasonRequest"]
    assert "expected_version" in versioned_reason["required"]
    transfer = spec["paths"]["/memberships/{membershipId}/unit"]["put"]
    request = transfer["requestBody"]["content"]["application/json"]["schema"]
    assert "expected_version" in request["required"]
    upsert = spec["components"]["schemas"]["UpsertUnitRequest"]
    conditional = upsert["allOf"][0]
    assert "unit_id" in conditional["if"]["required"]
    assert "expected_version" in conditional["then"]["required"]
    assert upsert["properties"]["expected_version"]["type"] == "integer"


def test_organization_operation_ids_are_unique() -> None:
    spec = _spec()
    operation_ids = [
        operation["operationId"]
        for path_item in spec["paths"].values()
        for method, operation in path_item.items()
        if method in {"get", "post", "put", "patch", "delete"}
    ]
    assert len(operation_ids) == len(set(operation_ids))


def test_organization_state_machines_cover_l0_through_l2() -> None:
    document = STATE_MACHINE_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Tenant",
        "## 2. Enterprise",
        "## 3. Organization Unit",
        "## 4. Membership",
        "## 5. 并发",
    ):
        assert heading in document
    assert "ORG_VERSION_CONFLICT" in document
    assert "ORG_UNIT_CYCLE_DETECTED" in document
