"""Release manifest and OpenAPI catalog helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_ROOT = Path(__file__).resolve().parents[2]
_MANIFEST = _ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"


def load_release_manifest(path: Path | None = None) -> dict[str, Any]:
    target = path or _MANIFEST
    loaded = yaml.safe_load(target.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("release manifest must be a mapping")
    return loaded


def list_openapi_contracts(path: Path | None = None) -> list[str]:
    manifest = load_release_manifest(path)
    contracts = manifest.get("openapi_contracts", [])
    if not isinstance(contracts, list):
        raise ValueError("openapi_contracts must be a list")
    return [str(item) for item in contracts]
