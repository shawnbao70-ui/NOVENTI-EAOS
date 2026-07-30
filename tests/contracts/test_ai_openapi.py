"""Normative PHX-A12 AI Runtime OpenAPI contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
OPENAPI_PATH = ROOT / "docs" / "api" / "ai.openapi.yaml"
STATE_MACHINE_PATH = ROOT / "docs" / "architecture" / "AI_RUNTIME_STATE_MACHINES.md"


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


def test_ai_openapi_is_versioned_and_complete() -> None:
    spec = _spec()
    assert spec["openapi"] == "3.1.0"
    assert {
        "/ai/status",
        "/ai/runs",
        "/ai/runs/{runId}",
        "/ai/tools",
        "/ai/runs/{runId}/tools/invocations",
        "/ai/runs/{runId}/memory",
        "/ai/runs/{runId}/memory/{key}",
        "/ai/runs/{runId}/approvals",
        "/ai/runs/{runId}/commits",
    } <= set(spec["paths"])


def test_ai_openapi_references_resolve() -> None:
    spec = _spec()
    for node in _walk(spec):
        ref = node.get("$ref")
        if ref is not None:
            _resolve_ref(spec, ref)


def test_ai_requests_cannot_assert_execution_context() -> None:
    forbidden = {
        "execution_context",
        "tenant_id",
        "session_id",
        "platform_scope",
        "subject_id",
    }
    spec = _spec()
    for name, schema in spec["components"]["schemas"].items():
        if name.endswith("Request"):
            assert forbidden.isdisjoint(schema.get("properties", {}))
            assert schema.get("additionalProperties") is False


def test_ai_state_machine_documents_approval_bridge() -> None:
    text = STATE_MACHINE_PATH.read_text(encoding="utf-8")
    assert "pending_approval" in text
    assert "CommitAction" in text
    assert "RequestApproval" in text
