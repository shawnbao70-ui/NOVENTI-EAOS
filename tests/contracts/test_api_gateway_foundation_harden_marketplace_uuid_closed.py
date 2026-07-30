"""Foundation harden — Marketplace UuidResult/BooleanResult response_model wire."""

from __future__ import annotations

from fastapi.routing import APIRoute

from api.gateway.app import create_app
from api.gateway.schemas.common import BooleanResult, UuidResult


def _route(path: str, method: str) -> APIRoute:
    app = create_app()
    for route in app.routes:
        if isinstance(route, APIRoute) and route.path == path and method in route.methods:
            return route
    raise AssertionError(f"missing route {method} {path}")


def test_marketplace_create_listing_uuid_result() -> None:
    assert _route("/v1/marketplace/listings", "POST").response_model is UuidResult


def test_marketplace_lifecycle_boolean_results() -> None:
    for path in (
        "/v1/marketplace/listings/{listing_id}/signature",
        "/v1/marketplace/listings/{listing_id}/submit",
        "/v1/marketplace/listings/{listing_id}/publish",
        "/v1/marketplace/listings/{listing_id}/revoke",
        "/v1/marketplace/listings/{listing_id}/pricing",
        "/v1/marketplace/listings/{listing_id}/revenue-share",
        "/v1/marketplace/disputes/{dispute_id}/resolve",
    ):
        assert _route(path, "POST").response_model is BooleanResult


def test_marketplace_acquire_invoice_dispute_uuid_results() -> None:
    for path in (
        "/v1/marketplace/listings/{listing_id}/acquire",
        "/v1/marketplace/listings/{listing_id}/invoices",
        "/v1/marketplace/listings/{listing_id}/disputes",
    ):
        assert _route(path, "POST").response_model is UuidResult


def test_permission_policy_grant_uuid_and_ok() -> None:
    from api.gateway.schemas.common import OkResponse

    assert _route("/v1/permission/policies", "POST").response_model is UuidResult
    assert _route("/v1/permission/grants", "POST").response_model is UuidResult
    assert (
        _route("/v1/permission/policies/{policy_id}/activation", "POST").response_model
        is OkResponse
    )
    assert (
        _route("/v1/terminal/previews", "POST").response_model is UuidResult
    )
    assert (
        _route("/v1/terminal/extensions/{extension_id}/activate", "POST").response_model
        is BooleanResult
    )


def test_event_and_workflow_uuid_ok_wire() -> None:
    from api.gateway.schemas.common import OkResponse

    assert _route("/v1/events/outbox", "POST").response_model is UuidResult
    assert _route("/v1/events/subscriptions", "POST").response_model is UuidResult
    assert _route("/v1/workflow/definitions", "POST").response_model is UuidResult
    assert (
        _route("/v1/workflow/definitions/{definition_id}/deprecation", "POST").response_model
        is OkResponse
    )


def test_knowledge_and_identity_uuid_ok_wire() -> None:
    from api.gateway.schemas.common import OkResponse

    assert _route("/v1/knowledge/entities", "POST").response_model is UuidResult
    assert _route("/v1/knowledge/links", "POST").response_model is UuidResult
    assert (
        _route("/v1/knowledge/entities/{entity_id}/archive", "POST").response_model
        is OkResponse
    )
    assert _route("/v1/identity/subjects", "POST").response_model is UuidResult
    assert _route("/v1/identity/credentials", "POST").response_model is UuidResult
    assert _route("/v1/identity/ai-employees", "POST").response_model is UuidResult


def test_organization_uuid_ok_wire() -> None:
    from api.gateway.schemas.common import OkResponse

    assert _route("/v1/enterprises", "POST").response_model is UuidResult
    assert _route("/v1/organization-units", "PUT").response_model is UuidResult
    assert _route("/v1/memberships", "POST").response_model is UuidResult
    assert (
        _route("/v1/enterprises/{enterprise_id}/suspension", "POST").response_model
        is OkResponse
    )
    assert _route("/v1/platform/tenants", "POST").response_model is UuidResult


def test_organization_openapi_create_paths_use_uuid_result() -> None:
    from pathlib import Path

    import yaml

    root = Path(__file__).resolve().parents[2]
    doc = yaml.safe_load(
        (root / "docs" / "api" / "organization.openapi.yaml").read_text(encoding="utf-8")
    )
    schemas = doc["components"]["schemas"]
    assert "IdResponse" not in schemas
    assert schemas["UuidResult"].get("additionalProperties") is False
    for path, method, code in (
        ("/platform/tenants", "post", "201"),
        ("/enterprises", "post", "201"),
        ("/organization-units", "put", "200"),
        ("/memberships", "post", "201"),
    ):
        ref = doc["paths"][path][method]["responses"][code]["content"][
            "application/json"
        ]["schema"]["$ref"]
        assert ref.endswith("/UuidResult"), (path, method, ref)


def test_permission_evaluate_explanation_closed_wire() -> None:
    from api.gateway.schemas.permission import DecisionExplanation, EvaluateResult

    assert _route("/v1/permission/evaluations", "POST").response_model is EvaluateResult
    assert (
        _route("/v1/permission/decisions/{decision_id}/explanation", "GET").response_model
        is DecisionExplanation
    )


def test_ai_brain_twin_uuid_wire_fail_closed_untouched() -> None:
    from api.gateway.schemas.common import OkResponse

    assert _route("/v1/ai/runs", "POST").response_model is UuidResult
    assert _route("/v1/ai/tools", "POST").response_model is UuidResult
    assert _route("/v1/ai/runs/{run_id}/commits", "POST").response_model is OkResponse
    assert _route("/v1/brain/insights", "POST").response_model is UuidResult
    assert _route("/v1/twin/snapshots", "POST").response_model is UuidResult
    # Fail-closed execute/authorize must not advertise success UuidResult/OkResponse.
    execute_model = _route(
        "/v1/brain/insights/{insight_id}/execute", "POST"
    ).response_model
    authorize_model = _route(
        "/v1/twin/snapshots/{snapshot_id}/authorize", "POST"
    ).response_model
    assert execute_model not in {UuidResult, OkResponse}
    assert authorize_model not in {UuidResult, OkResponse}


def test_event_closed_report_envelopes() -> None:
    from api.gateway.schemas.event import (
        DeadLetterListEnvelope,
        DeliveryReportResult,
        DeliveryStatsResult,
        DispatchReportResult,
        EventEnvelopeResponse,
        EventOkResponse,
    )

    assert _route("/v1/events", "POST").response_model is DeliveryReportResult
    assert _route("/v1/events/dispatch", "POST").response_model is DispatchReportResult
    assert _route("/v1/events/stats", "GET").response_model is DeliveryStatsResult
    assert (
        _route("/v1/events/dead-letters", "GET").response_model is DeadLetterListEnvelope
    )
    assert (
        _route("/v1/events/dead-letters/{dead_letter_id}/replay", "POST").response_model
        is EventOkResponse
    )
    assert _route("/v1/events/{event_id}", "GET").response_model is EventEnvelopeResponse
    assert (
        _route("/v1/events/{event_id}/replay", "POST").response_model
        is DeliveryReportResult
    )


def test_terminal_get_and_commit_closed_wire() -> None:
    from api.gateway.schemas.terminal import (
        ApprovalPresentationResponse,
        CommitReceiptResponse,
        PlanPreviewResponse,
        TerminalIntentResponse,
        TerminalSessionResponse,
    )

    assert (
        _route("/v1/terminal/sessions/{terminal_session_id}", "GET").response_model
        is TerminalSessionResponse
    )
    assert (
        _route("/v1/terminal/intents/{intent_id}", "GET").response_model
        is TerminalIntentResponse
    )
    assert (
        _route("/v1/terminal/previews/{preview_id}", "GET").response_model
        is PlanPreviewResponse
    )
    assert (
        _route("/v1/terminal/previews/{preview_id}/approvals", "GET").response_model
        is ApprovalPresentationResponse
    )
    assert (
        _route("/v1/terminal/previews/{preview_id}/commits", "POST").response_model
        is CommitReceiptResponse
    )


def test_package_and_marketplace_get_closed_wire() -> None:
    from api.gateway.schemas.marketplace import MarketplaceListingResponse
    from api.gateway.schemas.package import PackageManifestResponse

    assert (
        _route("/v1/packages/manifests/{manifest_id}", "GET").response_model
        is PackageManifestResponse
    )
    assert (
        _route("/v1/marketplace/listings/{listing_id}", "GET").response_model
        is MarketplaceListingResponse
    )


def test_marketplace_payment_and_host_acquire_closed_wire() -> None:
    from api.gateway.schemas.marketplace import HostAcquireResult, PaymentClearingEnvelope

    assert (
        _route(
            "/v1/marketplace/listings/{listing_id}/payment-clearing", "POST"
        ).response_model
        is PaymentClearingEnvelope
    )
    assert (
        _route("/v1/marketplace/listings/{listing_id}/host-acquire", "POST").response_model
        is HostAcquireResult
    )


def test_permission_effective_permissions_closed_wire() -> None:
    from api.gateway.schemas.permission import EffectivePermission

    assert (
        _route(
            "/v1/permission/principals/{subject_id}/effective-permissions", "GET"
        ).response_model
        == list[EffectivePermission]
    )


def test_org_workflow_brain_twin_get_closed_wire() -> None:
    from api.gateway.schemas.brain import BrainInsightResponse
    from api.gateway.schemas.organization import (
        EnterpriseResponse,
        MembershipResponse,
        OrganizationUnitResponse,
        TenantResponse,
    )
    from api.gateway.schemas.twin import TwinSnapshotResponse
    from api.gateway.schemas.workflow import WorkflowTaskResponse

    assert (
        _route("/v1/tenants/{tenant_id}", "GET").response_model is TenantResponse
    )
    assert _route("/v1/enterprises", "GET").response_model == list[EnterpriseResponse]
    assert (
        _route("/v1/enterprises/{enterprise_id}", "GET").response_model
        is EnterpriseResponse
    )
    assert (
        _route("/v1/organization-units/tree", "GET").response_model
        == list[OrganizationUnitResponse]
    )
    assert _route("/v1/memberships", "GET").response_model == list[MembershipResponse]
    assert _route("/v1/workflow/tasks", "GET").response_model == list[WorkflowTaskResponse]
    assert (
        _route("/v1/brain/insights/{insight_id}", "GET").response_model
        is BrainInsightResponse
    )
    assert (
        _route("/v1/twin/snapshots/{snapshot_id}", "GET").response_model
        is TwinSnapshotResponse
    )
    # Fail-closed surfaces remain without success entity response models.
    from api.gateway.schemas.common import OkResponse, UuidResult

    assert (
        _route("/v1/brain/insights/{insight_id}/execute", "POST").response_model
        not in {UuidResult, OkResponse, BrainInsightResponse}
    )
    assert (
        _route("/v1/twin/snapshots/{snapshot_id}/authorize", "POST").response_model
        not in {UuidResult, OkResponse, TwinSnapshotResponse}
    )


def test_knowledge_and_ai_get_closed_wire() -> None:
    from api.gateway.schemas.ai import (
        AgentRunResponse,
        MemoryEntryResponse,
        ToolInvocationResult,
    )
    from api.gateway.schemas.knowledge import (
        KnowledgeEntityListEnvelope,
        KnowledgeEntityResponse,
        ProvenanceListEnvelope,
    )

    assert (
        _route("/v1/knowledge/entities", "GET").response_model
        is KnowledgeEntityListEnvelope
    )
    assert (
        _route("/v1/knowledge/entities/{entity_id}", "GET").response_model
        is KnowledgeEntityResponse
    )
    assert (
        _route("/v1/knowledge/search", "GET").response_model
        is KnowledgeEntityListEnvelope
    )
    assert (
        _route("/v1/knowledge/provenance/{subject_kind}/{subject_id}", "GET").response_model
        is ProvenanceListEnvelope
    )
    assert _route("/v1/ai/runs/{run_id}", "GET").response_model is AgentRunResponse
    assert (
        _route("/v1/ai/runs/{run_id}/memory/{key}", "GET").response_model
        is MemoryEntryResponse
    )
    assert (
        _route("/v1/ai/runs/{run_id}/tools/invocations", "POST").response_model
        is ToolInvocationResult
    )


def test_identity_and_workflow_closed_wire() -> None:
    from api.gateway.schemas.identity import (
        AIEmployeeProfileResponse,
        CredentialValidationResponse,
        SessionCreatedResponse,
        SessionValidationResponse,
        SubjectResponse,
    )
    from api.gateway.schemas.workflow import (
        InstanceStatusResult,
        StartInstanceResult,
        WorkflowInstanceResponse,
    )

    assert (
        _route("/v1/identity/subjects/{subject_id}", "GET").response_model
        is SubjectResponse
    )
    assert (
        _route("/v1/identity/credentials/{credential_id}/validation", "GET").response_model
        is CredentialValidationResponse
    )
    assert _route("/v1/identity/sessions", "POST").response_model is SessionCreatedResponse
    assert (
        _route("/v1/identity/sessions/{session_id}/validation", "GET").response_model
        is SessionValidationResponse
    )
    assert (
        _route("/v1/identity/ai-employees/{ai_subject_id}/profile", "GET").response_model
        is AIEmployeeProfileResponse
    )
    assert _route("/v1/workflow/instances", "POST").response_model is StartInstanceResult
    assert (
        _route("/v1/workflow/instances/{instance_id}", "GET").response_model
        is WorkflowInstanceResponse
    )
    assert (
        _route("/v1/workflow/instances/{instance_id}/signals", "POST").response_model
        is InstanceStatusResult
    )
