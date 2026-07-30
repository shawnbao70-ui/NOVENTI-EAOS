"""Normative PHX-E15 Brain/Twin OpenAPI contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
OPENAPI_PATH = ROOT / "docs" / "api" / "brain.openapi.yaml"
STATE_MACHINE_PATH = ROOT / "docs" / "architecture" / "BRAIN_TWIN_STATE_MACHINES.md"


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


def test_brain_openapi_is_versioned_and_complete() -> None:
    spec = _spec()
    assert spec["openapi"] == "3.1.0"
    assert {
        "/twin/status",
        "/twin/snapshots",
        "/twin/snapshots/{snapshotId}",
        "/twin/snapshots/{snapshotId}/authorize",
        "/brain/status",
        "/brain/insights",
        "/brain/insights/{insightId}",
        "/brain/insights/{insightId}/execute",
    } <= set(spec["paths"])


def test_brain_openapi_references_resolve() -> None:
    spec = _spec()
    for node in _walk(spec):
        ref = node.get("$ref")
        if ref is not None:
            _resolve_ref(spec, ref)


def test_brain_openapi_marks_execution_paths_permission_gated() -> None:
    spec = _spec()
    authorize = spec["paths"]["/twin/snapshots/{snapshotId}/authorize"]["post"]
    execute = spec["paths"]["/brain/insights/{insightId}/execute"]["post"]
    assert "permission-gated" in authorize["summary"].casefold()
    assert "permission-gated" in execute["summary"].casefold()
    assert "200" in authorize["responses"]
    assert "403" in authorize["responses"]
    assert "200" in execute["responses"]
    assert "403" in execute["responses"]


def test_brain_state_machine_doc_exists() -> None:
    text = STATE_MACHINE_PATH.read_text(encoding="utf-8")
    assert "advisory" in text.casefold()
    assert "request_execution" in text
