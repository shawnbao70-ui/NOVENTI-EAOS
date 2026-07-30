"""Normative PHX-B14 Package Platform OpenAPI contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
OPENAPI_PATH = ROOT / "docs" / "api" / "package.openapi.yaml"
STATE_MACHINE_PATH = ROOT / "docs" / "architecture" / "PACKAGE_STATE_MACHINES.md"
SAMPLE_MANIFEST = ROOT / "packages" / "sample_ops" / "manifest.json"


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


def test_package_openapi_is_versioned_and_complete() -> None:
    spec = _spec()
    assert spec["openapi"] == "3.1.0"
    assert {
        "/packages/status",
        "/packages/manifests",
        "/packages/manifests/{manifestId}",
        "/packages/manifests/{manifestId}/publish",
        "/packages/installations",
        "/packages/installations/{installationId}/disable",
        "/packages/surfaces",
        "/packages/actions/resolve",
    } <= set(spec["paths"])


def test_package_openapi_references_resolve() -> None:
    spec = _spec()
    for node in _walk(spec):
        ref = node.get("$ref")
        if ref is not None:
            _resolve_ref(spec, ref)


def test_sample_ops_manifest_exists() -> None:
    assert SAMPLE_MANIFEST.is_file()
    text = SAMPLE_MANIFEST.read_text(encoding="utf-8")
    assert "noventi.sample.ops" in text
    assert "pkg.ops.brief" in text


def test_package_state_machine_doc_exists() -> None:
    text = STATE_MACHINE_PATH.read_text(encoding="utf-8")
    assert "published" in text
    assert "installed" in text
