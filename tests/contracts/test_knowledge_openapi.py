"""Normative PHX-K10 Knowledge OpenAPI and state-machine contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
OPENAPI_PATH = ROOT / "docs" / "api" / "knowledge.openapi.yaml"
STATE_MACHINE_PATH = ROOT / "docs" / "architecture" / "KNOWLEDGE_STATE_MACHINES.md"


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


def test_knowledge_openapi_is_versioned_and_complete() -> None:
    spec = _spec()
    assert spec["openapi"] == "3.1.0"
    assert spec["servers"] == [{"url": "/v1"}]
    assert spec["security"] == [{"bearerAuth": []}]
    assert {
        "/knowledge/status",
        "/knowledge/entities",
        "/knowledge/entities/{entityId}",
        "/knowledge/entities/{entityId}/archive",
        "/knowledge/entities/{entityId}/share",
        "/knowledge/links",
        "/knowledge/search",
        "/knowledge/provenance/{subjectKind}/{subjectId}",
    } <= set(spec["paths"])


def test_knowledge_openapi_references_resolve() -> None:
    spec = _spec()
    for node in _walk(spec):
        ref = node.get("$ref")
        if ref is not None:
            _resolve_ref(spec, ref)


def test_knowledge_requests_cannot_assert_execution_context() -> None:
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
        "subject_id",
    }
    for name, schema in spec["components"]["schemas"].items():
        if name.endswith("Request"):
            assert forbidden.isdisjoint(schema.get("properties", {}))
            assert schema.get("additionalProperties") is False


def test_knowledge_state_machine_documents_retention() -> None:
    text = STATE_MACHINE_PATH.read_text(encoding="utf-8")
    assert "active --> archived" in text
    assert "derived" in text.casefold()
    assert "retain_until" in text
