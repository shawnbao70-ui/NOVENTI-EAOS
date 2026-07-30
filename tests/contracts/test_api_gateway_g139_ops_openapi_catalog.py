"""PHX-G139 Gateway Ops OpenAPI Catalog contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from eaos_sdk import list_openapi_contracts

ROOT = Path(__file__).resolve().parents[2]
OPS_OPENAPI = ROOT / "docs" / "api" / "ops.openapi.yaml"
MANIFEST = ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_ops_openapi_registered_in_release_inventory() -> None:
    relative = "docs/api/ops.openapi.yaml"
    contracts = list_openapi_contracts()
    assert relative in contracts
    assert len(contracts) == 14
    manifest = _load_yaml(MANIFEST)
    assert relative in manifest["openapi_contracts"]
    assert OPS_OPENAPI.is_file()


def test_ops_openapi_catalog_matches_gateway_meta_paths() -> None:
    spec = _load_yaml(OPS_OPENAPI)
    for path in ("/health", "/release", "/adapters", "/context"):
        assert "get" in spec["paths"][path]
    assert "post" in spec["paths"]["/context/echo"]
    assert spec["paths"]["/health"]["get"].get("security") == []
    assert spec["paths"]["/release"]["get"].get("security") == []
    assert spec["paths"]["/adapters"]["get"].get("security") == []
