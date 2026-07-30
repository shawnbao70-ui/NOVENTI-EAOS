"""Normative PHX-M16 Marketplace OpenAPI contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
OPENAPI_PATH = ROOT / "docs" / "api" / "marketplace.openapi.yaml"
STATE_MACHINE_PATH = ROOT / "docs" / "architecture" / "MARKETPLACE_STATE_MACHINES.md"


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


def test_marketplace_openapi_is_versioned_and_complete() -> None:
    spec = _spec()
    assert spec["openapi"] == "3.1.0"
    assert {
        "/marketplace/status",
        "/marketplace/listings",
        "/marketplace/listings/{listingId}",
        "/marketplace/listings/{listingId}/signature",
        "/marketplace/listings/{listingId}/submit",
        "/marketplace/listings/{listingId}/review",
        "/marketplace/listings/{listingId}/publish",
        "/marketplace/listings/{listingId}/revoke",
        "/marketplace/listings/{listingId}/acquire",
        "/marketplace/listings/{listingId}/pricing",
        "/marketplace/listings/{listingId}/invoices",
        "/marketplace/listings/{listingId}/disputes",
        "/marketplace/listings/{listingId}/revenue-share",
        "/marketplace/disputes/{disputeId}/resolve",
    } <= set(spec["paths"])


def test_marketplace_openapi_references_resolve() -> None:
    spec = _spec()
    for node in _walk(spec):
        ref = node.get("$ref")
        if ref is not None:
            _resolve_ref(spec, ref)


def test_marketplace_pricing_path_foundation_policy() -> None:
    summary = _spec()["paths"]["/marketplace/listings/{listingId}/pricing"]["post"]["summary"]
    assert "foundation" in summary.casefold() or "fixed" in summary.casefold()


def test_marketplace_state_machine_doc_exists() -> None:
    text = STATE_MACHINE_PATH.read_text(encoding="utf-8")
    assert "published" in text
    assert "revoked" in text
