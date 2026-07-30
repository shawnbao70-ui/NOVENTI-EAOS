"""Normative PHX-P11 Event OpenAPI and state-machine contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
OPENAPI_PATH = ROOT / "docs" / "api" / "event.openapi.yaml"
STATE_MACHINE_PATH = ROOT / "docs" / "architecture" / "EVENT_STATE_MACHINES.md"


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


def test_event_openapi_is_versioned_and_complete() -> None:
    spec = _spec()
    assert spec["openapi"] == "3.1.0"
    assert {
        "/events",
        "/events/outbox",
        "/events/dispatch",
        "/events/{eventId}",
        "/events/{eventId}/replay",
        "/events/subscriptions",
        "/events/stats",
        "/events/dead-letters",
        "/events/dead-letters/{deadLetterId}/replay",
    } <= set(spec["paths"])


def test_event_openapi_references_resolve() -> None:
    spec = _spec()
    for node in _walk(spec):
        ref = node.get("$ref")
        if ref is not None:
            _resolve_ref(spec, ref)


def test_event_requests_cannot_assert_execution_context() -> None:
    spec = _spec()
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


def test_event_state_machine_documents_outbox_and_dlq() -> None:
    text = STATE_MACHINE_PATH.read_text(encoding="utf-8")
    assert "pending --> leased" in text
    assert "failed --> dead" in text
    assert "ReplayDeadLetter" in text
