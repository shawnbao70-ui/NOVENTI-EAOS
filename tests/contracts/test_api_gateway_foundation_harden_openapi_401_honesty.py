"""Foundation harden — OpenAPI 401 honesty on bearer-gated surfaces."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def _load(name: str) -> dict:
    return yaml.safe_load((ROOT / "docs" / "api" / name).read_text(encoding="utf-8"))


def _assert_401(responses: dict) -> None:
    assert "401" in responses
    ref = responses["401"]["content"]["application/json"]["schema"]["$ref"]
    assert "GatewayDetailError" in ref


def test_platform_roles_document_401() -> None:
    paths = _load("platform.openapi.yaml")["paths"]
    _assert_401(paths["/platform/roles"]["get"]["responses"])
    _assert_401(paths["/platform/roles"]["post"]["responses"])


def test_terminal_sessions_document_401() -> None:
    paths = _load("terminal.openapi.yaml")["paths"]
    _assert_401(paths["/terminal/sessions"]["post"]["responses"])


def test_permission_grants_document_401() -> None:
    paths = _load("permission.openapi.yaml")["paths"]
    _assert_401(paths["/permission/grants"]["post"]["responses"])


def test_package_manifests_document_401() -> None:
    paths = _load("package.openapi.yaml")["paths"]
    _assert_401(paths["/packages/manifests"]["post"]["responses"])


def test_marketplace_listings_document_401() -> None:
    paths = _load("marketplace.openapi.yaml")["paths"]
    _assert_401(paths["/marketplace/listings"]["post"]["responses"])


def test_terminal_intents_document_401() -> None:
    paths = _load("terminal.openapi.yaml")["paths"]
    _assert_401(paths["/terminal/intents"]["post"]["responses"])


def test_permission_policies_document_401() -> None:
    paths = _load("permission.openapi.yaml")["paths"]
    _assert_401(paths["/permission/policies"]["post"]["responses"])


def test_event_outbox_document_401() -> None:
    paths = _load("event.openapi.yaml")["paths"]
    _assert_401(paths["/events/outbox"]["post"]["responses"])


def test_workflow_definitions_document_401() -> None:
    paths = _load("workflow.openapi.yaml")["paths"]
    _assert_401(paths["/workflow/definitions"]["post"]["responses"])


def test_knowledge_entities_document_401() -> None:
    paths = _load("knowledge.openapi.yaml")["paths"]
    _assert_401(paths["/knowledge/entities"]["post"]["responses"])


def test_identity_subjects_document_401() -> None:
    paths = _load("identity.openapi.yaml")["paths"]
    _assert_401(paths["/identity/subjects"]["post"]["responses"])


def test_organization_enterprises_document_401() -> None:
    paths = _load("organization.openapi.yaml")["paths"]
    _assert_401(paths["/enterprises"]["post"]["responses"])


def test_ai_runs_document_401() -> None:
    paths = _load("ai.openapi.yaml")["paths"]
    _assert_401(paths["/ai/runs"]["post"]["responses"])


def test_brain_insights_and_twin_snapshots_document_401() -> None:
    paths = _load("brain.openapi.yaml")["paths"]
    _assert_401(paths["/brain/insights"]["post"]["responses"])
    _assert_401(paths["/twin/snapshots"]["post"]["responses"])


def test_permission_evaluations_document_401() -> None:
    paths = _load("permission.openapi.yaml")["paths"]
    _assert_401(paths["/permission/evaluations"]["post"]["responses"])


def test_event_publish_and_dispatch_document_401() -> None:
    paths = _load("event.openapi.yaml")["paths"]
    _assert_401(paths["/events"]["post"]["responses"])
    _assert_401(paths["/events/dispatch"]["post"]["responses"])


def test_terminal_session_get_document_401() -> None:
    paths = _load("terminal.openapi.yaml")["paths"]
    _assert_401(paths["/terminal/sessions/{terminalSessionId}"]["get"]["responses"])


def test_package_manifest_get_document_401() -> None:
    paths = _load("package.openapi.yaml")["paths"]
    _assert_401(paths["/packages/manifests/{manifestId}"]["get"]["responses"])


def test_marketplace_listing_get_document_401() -> None:
    paths = _load("marketplace.openapi.yaml")["paths"]
    _assert_401(paths["/marketplace/listings/{listingId}"]["get"]["responses"])


def test_identity_subject_get_document_401() -> None:
    paths = _load("identity.openapi.yaml")["paths"]
    _assert_401(paths["/identity/subjects/{subjectId}"]["get"]["responses"])


def test_workflow_instances_document_401() -> None:
    paths = _load("workflow.openapi.yaml")["paths"]
    _assert_401(paths["/workflow/instances"]["post"]["responses"])


def test_knowledge_entity_get_document_401() -> None:
    paths = _load("knowledge.openapi.yaml")["paths"]
    _assert_401(paths["/knowledge/entities/{entityId}"]["get"]["responses"])


def test_ai_run_get_document_401() -> None:
    paths = _load("ai.openapi.yaml")["paths"]
    _assert_401(paths["/ai/runs/{runId}"]["get"]["responses"])


def test_organization_tenant_get_document_401() -> None:
    paths = _load("organization.openapi.yaml")["paths"]
    _assert_401(paths["/tenants/{tenantId}"]["get"]["responses"])


def test_workflow_tasks_document_401() -> None:
    paths = _load("workflow.openapi.yaml")["paths"]
    _assert_401(paths["/workflow/tasks"]["get"]["responses"])


def test_brain_insight_and_twin_snapshot_get_document_401() -> None:
    paths = _load("brain.openapi.yaml")["paths"]
    _assert_401(paths["/brain/insights/{insightId}"]["get"]["responses"])
    _assert_401(paths["/twin/snapshots/{snapshotId}"]["get"]["responses"])


def test_permission_effective_permissions_document_401() -> None:
    paths = _load("permission.openapi.yaml")["paths"]
    _assert_401(
        paths["/permission/principals/{subjectId}/effective-permissions"]["get"][
            "responses"
        ]
    )


def test_organization_enterprises_list_document_401() -> None:
    paths = _load("organization.openapi.yaml")["paths"]
    _assert_401(paths["/enterprises"]["get"]["responses"])


def test_marketplace_payment_clearing_and_host_acquire_document_401() -> None:
    paths = _load("marketplace.openapi.yaml")["paths"]
    _assert_401(
        paths["/marketplace/listings/{listingId}/payment-clearing"]["post"]["responses"]
    )
    _assert_401(
        paths["/marketplace/listings/{listingId}/host-acquire"]["post"]["responses"]
    )


_PUBLIC_PATHS = frozenset(
    {
        "/health",
        "/release",
        "/adapters",
        "/auth/login",
        "/auth/callback",
        "/auth/providers",
        "/auth/status",
        "/auth/oidc/providers",
        "/auth/oidc/mfa-enrollment",
        "/auth/webauthn/register/options",
        "/auth/webauthn/register/verify",
        "/auth/webauthn/authenticate/options",
        "/auth/webauthn/authenticate/verify",
        "/auth/mfa-enrollment",
    }
)


def _is_public_path(path: str) -> bool:
    if path in _PUBLIC_PATHS or path.startswith("/ops/"):
        return True
    # Foundation posture endpoints are unauthenticated except roles/status.
    if path.endswith("/status") and "roles/status" not in path:
        return True
    return False


def _iter_auth_gated_2xx_ops(spec_name: str) -> list[tuple[str, str]]:
    doc = _load(spec_name)
    out: list[tuple[str, str]] = []
    for path, methods in (doc.get("paths") or {}).items():
        if _is_public_path(path):
            continue
        for method, op in (methods or {}).items():
            if method.startswith("x-") or not isinstance(op, dict):
                continue
            # Explicit public override in OpenAPI.
            if op.get("security") == []:
                continue
            responses = op.get("responses") or {}
            if any(str(code).startswith("2") for code in responses):
                out.append((path, method))
    return out


def test_platform_idp_and_role_disable_document_401() -> None:
    paths = _load("platform.openapi.yaml")["paths"]
    for path, method in _iter_auth_gated_2xx_ops("platform.openapi.yaml"):
        _assert_401(paths[path][method]["responses"])


def test_marketplace_lifecycle_and_commercial_document_401() -> None:
    paths = _load("marketplace.openapi.yaml")["paths"]
    for path, method in _iter_auth_gated_2xx_ops("marketplace.openapi.yaml"):
        _assert_401(paths[path][method]["responses"])


def test_terminal_preview_approval_extension_document_401() -> None:
    paths = _load("terminal.openapi.yaml")["paths"]
    for path, method in _iter_auth_gated_2xx_ops("terminal.openapi.yaml"):
        _assert_401(paths[path][method]["responses"])


def test_organization_mutate_and_memberships_document_401() -> None:
    paths = _load("organization.openapi.yaml")["paths"]
    for path, method in _iter_auth_gated_2xx_ops("organization.openapi.yaml"):
        _assert_401(paths[path][method]["responses"])


def test_identity_credentials_sessions_ai_document_401() -> None:
    paths = _load("identity.openapi.yaml")["paths"]
    for path, method in _iter_auth_gated_2xx_ops("identity.openapi.yaml"):
        _assert_401(paths[path][method]["responses"])


def test_remaining_foundation_specs_auth_gated_2xx_document_401() -> None:
    """Sweep Permission/Event/Workflow/AI/Knowledge/Package (+ brain/twin 2xx)."""
    for spec in (
        "permission.openapi.yaml",
        "event.openapi.yaml",
        "workflow.openapi.yaml",
        "ai.openapi.yaml",
        "knowledge.openapi.yaml",
        "package.openapi.yaml",
        "brain.openapi.yaml",
    ):
        paths = _load(spec)["paths"]
        gated = _iter_auth_gated_2xx_ops(spec)
        assert gated, f"expected auth-gated ops in {spec}"
        for path, method in gated:
            _assert_401(paths[path][method]["responses"])


def test_brain_execute_and_twin_authorize_fail_closed_document_401() -> None:
    """Fail-closed paths have no 2xx; still document tenant auth required."""
    paths = _load("brain.openapi.yaml")["paths"]
    execute = paths["/brain/insights/{insightId}/execute"]["post"]["responses"]
    authorize = paths["/twin/snapshots/{snapshotId}/authorize"]["post"]["responses"]
    _assert_401(execute)
    _assert_401(authorize)
    assert "200" not in execute and "201" not in execute
    assert "200" not in authorize and "201" not in authorize
    assert "403" in execute and "403" in authorize
