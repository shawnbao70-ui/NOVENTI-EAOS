"""PHX-G131 Auth OpenAPI Status Catalog contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from eaos_sdk import list_openapi_contracts

ROOT = Path(__file__).resolve().parents[2]
AUTH_OPENAPI = ROOT / "docs" / "api" / "auth.openapi.yaml"
MANIFEST = ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_auth_openapi_registered_in_release_inventory() -> None:
    relative = "docs/api/auth.openapi.yaml"
    contracts = list_openapi_contracts()
    assert relative in contracts
    assert len(contracts) >= 12
    manifest = _load_yaml(MANIFEST)
    assert relative in manifest["openapi_contracts"]
    assert AUTH_OPENAPI.is_file()


def test_auth_openapi_status_catalog_matches_gateway_paths() -> None:
    spec = _load_yaml(AUTH_OPENAPI)
    required = {
        "/auth/oidc/status",
        "/auth/idp/status",
        "/auth/jwt/status",
    }
    assert required <= set(spec["paths"])
    for path in required:
        assert "get" in spec["paths"][path]
        assert spec["paths"][path]["get"]["security"] == []
