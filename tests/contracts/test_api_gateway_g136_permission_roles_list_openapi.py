"""PHX-G136 Permission Roles List OpenAPI contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
PERMISSION_OPENAPI = ROOT / "docs" / "api" / "permission.openapi.yaml"


def _spec() -> dict[str, Any]:
    loaded = yaml.safe_load(PERMISSION_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _resolve_ref(spec: dict[str, Any], ref: str) -> Any:
    assert ref.startswith("#/")
    value: Any = spec
    for segment in ref[2:].split("/"):
        value = value[segment]
    return value


def test_permission_openapi_documents_roles_list() -> None:
    spec = _spec()
    assert str(spec["info"]["version"]).startswith("1.1.")
    operation = spec["paths"]["/permission/roles"]["get"]
    assert operation["operationId"] == "listPermissionRoles"
    assert "200" in operation["responses"]
    assert "503" in operation["responses"]
    schema_ref = operation["responses"]["200"]["content"]["application/json"][
        "schema"
    ]["$ref"]
    assert schema_ref.endswith("PermissionRoleCatalogResponse")
    payload = _resolve_ref(spec, schema_ref)
    assert set(payload["required"]) == {"enabled", "roles"}
    assert "data" not in payload.get("properties", {})


def test_permission_roles_list_is_not_role_grant_auto_write() -> None:
    body = PERMISSION_OPENAPI.read_text(encoding="utf-8")
    assert "Role→grant" in body or "Role->grant" in body
    assert "/platform/roles" in body
    paths = set(_spec()["paths"])
    assert "/permission/roles" in paths
    # G136/G146 held path ABSENT; G156 stub; G161 env-gated mint (default 503).
    if "/permission/role-grants" in paths:
        assert "GATEWAY_ROLE_GRANT_AUTO_WRITE_DISABLED" in body or "503" in body
        assert (
            "stub" in body.casefold()
            or "G156" in body
            or "G161" in body
            or "EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED" in body
        )
    assert "role_grant_product" in body or "auto_grant_from_role_enabled" in body
    status_props = _spec()["components"]["schemas"]["RoleCatalogStatus"]["properties"]
    assert "role_grant_product" in status_props
    product = _spec()["components"]["schemas"]["RoleGrantProductPosture"]["properties"]
    assert product["auto_grant_from_role_enabled"].get("type") == "boolean" or (
        product["auto_grant_from_role_enabled"].get("const") is False
    )
