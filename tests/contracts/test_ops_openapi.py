"""Normative PHX-G139 Gateway Ops OpenAPI contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
OPENAPI_PATH = ROOT / "docs" / "api" / "ops.openapi.yaml"


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


def test_ops_openapi_is_versioned_and_complete() -> None:
    spec = _spec()
    assert spec["openapi"] == "3.1.0"
    assert spec["servers"] == [{"url": "/v1"}]
    assert spec["security"] == []
    assert spec["info"]["version"].startswith("1.0.")
    assert {
        "/health",
        "/release",
        "/adapters",
        "/context",
        "/context/echo",
    } <= set(spec["paths"])


def test_ops_openapi_references_resolve() -> None:
    spec = _spec()
    for node in _walk(spec):
        ref = node.get("$ref")
        if ref is not None:
            _resolve_ref(spec, ref)


def test_ops_echo_documents_elevation_rejection() -> None:
    spec = _spec()
    echo = spec["paths"]["/context/echo"]["post"]
    assert "400" in echo["responses"]
    description = (echo.get("description") or "") + (spec["info"].get("description") or "")
    assert "platform_scope" in description
    assert "tenant_id" in description
