"""Normative PHX-T13 Smart Terminal OpenAPI contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
OPENAPI_PATH = ROOT / "docs" / "api" / "terminal.openapi.yaml"
STATE_MACHINE_PATH = ROOT / "docs" / "architecture" / "SMART_TERMINAL_STATE_MACHINES.md"


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


def test_terminal_openapi_is_versioned_and_complete() -> None:
    spec = _spec()
    assert spec["openapi"] == "3.1.0"
    assert {
        "/terminal/sessions",
        "/terminal/sessions/{terminalSessionId}",
        "/terminal/intents",
        "/terminal/intents/{intentId}",
        "/terminal/previews",
        "/terminal/previews/{previewId}",
        "/terminal/previews/{previewId}/approvals",
        "/terminal/previews/{previewId}/commits",
    } <= set(spec["paths"])


def test_terminal_openapi_references_resolve() -> None:
    spec = _spec()
    for node in _walk(spec):
        ref = node.get("$ref")
        if ref is not None:
            _resolve_ref(spec, ref)


def test_terminal_openapi_forbids_client_security_context_fields() -> None:
    spec = _spec()
    body = spec["components"]["schemas"]["OpenSessionRequest"]["properties"]
    assert "tenant_id" not in body
    assert "subject_id" not in body
    assert "platform_scope" not in body
    assert "session_id" not in body


def test_terminal_state_machine_doc_exists() -> None:
    text = STATE_MACHINE_PATH.read_text(encoding="utf-8")
    assert "active" in text
    assert "committed" in text
    assert "Workflow" in text
