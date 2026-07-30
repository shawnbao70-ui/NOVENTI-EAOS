"""PHX-G135 Platform OpenAPI Catalog contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from eaos_sdk import list_openapi_contracts

ROOT = Path(__file__).resolve().parents[2]
PLATFORM_OPENAPI = ROOT / "docs" / "api" / "platform.openapi.yaml"
MANIFEST = ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_platform_openapi_registered_in_release_inventory() -> None:
    relative = "docs/api/platform.openapi.yaml"
    contracts = list_openapi_contracts()
    assert relative in contracts
    assert len(contracts) >= 13
    manifest = _load_yaml(MANIFEST)
    assert relative in manifest["openapi_contracts"]
    assert PLATFORM_OPENAPI.is_file()


def test_platform_openapi_catalog_matches_gateway_paths() -> None:
    spec = _load_yaml(PLATFORM_OPENAPI)
    assert "get" in spec["paths"]["/platform/roles"]
    assert "post" in spec["paths"]["/platform/roles"]
    assert "post" in spec["paths"]["/platform/roles/{roleId}/disable"]
    assert "get" in spec["paths"]["/platform/idp/issuers"]
    assert "post" in spec["paths"]["/platform/idp/issuers"]
    assert "get" in spec["paths"]["/platform/idp/federation/matrix"]
    assert "post" in spec["paths"][
        "/platform/idp/federation/bindings/{bindingId}/priority"
    ]
    assert "get" in spec["paths"]["/platform/digital-employee/status"]
    assert "get" in spec["paths"]["/platform/industry-package/status"]
    assert "get" in spec["paths"]["/platform/ai-workforce/status"]
    # Organization tenant lifecycle remains outside this catalog
    assert "/platform/tenants" not in spec["paths"]
