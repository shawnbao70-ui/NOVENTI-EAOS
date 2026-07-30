"""PHX-G130 OpenAPI Foundation Status Catalog contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
API = ROOT / "docs" / "api"

STATUS_CATALOG: dict[str, set[str]] = {
    "identity.openapi.yaml": {"/identity/status"},
    "organization.openapi.yaml": {"/organization/status"},
    "permission.openapi.yaml": {"/permission/roles/status"},
    "workflow.openapi.yaml": {"/workflow/status"},
    "knowledge.openapi.yaml": {"/knowledge/status"},
    "package.openapi.yaml": {"/packages/status"},
    "terminal.openapi.yaml": {"/terminal/status"},
    "event.openapi.yaml": {"/events/status"},
    "brain.openapi.yaml": {"/twin/status", "/brain/status"},
    "ai.openapi.yaml": {"/ai/status"},
    "marketplace.openapi.yaml": {"/marketplace/status"},
}


def _load(name: str) -> dict[str, Any]:
    loaded = yaml.safe_load((API / name).read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _resolve_ref(spec: dict[str, Any], ref: str) -> Any:
    assert ref.startswith("#/")
    value: Any = spec
    for segment in ref[2:].split("/"):
        value = value[segment]
    return value


def test_openapi_foundation_status_catalog_paths_present() -> None:
    for filename, required in STATUS_CATALOG.items():
        spec = _load(filename)
        assert required <= set(spec["paths"]), filename


def test_openapi_foundation_status_gets_are_documented() -> None:
    for filename, required in STATUS_CATALOG.items():
        spec = _load(filename)
        for path in required:
            operation = spec["paths"][path]["get"]
            assert operation.get("operationId")
            schema_ref = operation["responses"]["200"]["content"]["application/json"][
                "schema"
            ]["$ref"]
            schema = _resolve_ref(spec, schema_ref)
            assert schema["required"] == ["data"]
            data_ref = schema["properties"]["data"]["$ref"]
            data_schema = _resolve_ref(spec, data_ref)
            assert "properties" in data_schema
