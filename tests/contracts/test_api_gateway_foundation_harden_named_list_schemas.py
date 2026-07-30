"""Foundation harden — named bare-array list success schemas (OpenAPI-first)."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
API = ROOT / "docs" / "api"


def _load(name: str) -> dict:
    return yaml.safe_load((API / name).read_text(encoding="utf-8"))


def _assert_named_array(doc: dict, schema_name: str, item_name: str) -> None:
    schema = doc["components"]["schemas"][schema_name]
    assert schema["type"] == "array"
    assert schema["items"]["$ref"].endswith(f"/{item_name}")


def test_organization_list_paths_use_named_array_schemas() -> None:
    doc = _load("organization.openapi.yaml")
    _assert_named_array(doc, "EnterpriseList", "Enterprise")
    _assert_named_array(doc, "OrganizationUnitList", "OrganizationUnit")
    _assert_named_array(doc, "MembershipList", "Membership")
    paths = doc["paths"]
    assert paths["/enterprises"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]["$ref"].endswith("/EnterpriseList")
    assert paths["/organization-units/tree"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]["$ref"].endswith("/OrganizationUnitList")
    assert paths["/memberships"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]["$ref"].endswith("/MembershipList")


def test_workflow_tasks_and_effective_permissions_named_lists() -> None:
    workflow = _load("workflow.openapi.yaml")
    permission = _load("permission.openapi.yaml")
    _assert_named_array(workflow, "WorkflowTaskList", "WorkflowTask")
    _assert_named_array(permission, "EffectivePermissionList", "EffectivePermission")
    assert workflow["paths"]["/workflow/tasks"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]["$ref"].endswith("/WorkflowTaskList")
    assert permission["paths"][
        "/permission/principals/{subjectId}/effective-permissions"
    ]["get"]["responses"]["200"]["content"]["application/json"]["schema"][
        "$ref"
    ].endswith("/EffectivePermissionList")
