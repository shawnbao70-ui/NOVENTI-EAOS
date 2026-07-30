"""Smart Terminal HTTP surface — thin transport adapter (PHX-G30)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from api.gateway.context import derive_tenant_context, reject_context_override
from api.gateway.deps import (
    PackageGatewayService,
    TerminalGatewayService,
    get_package_service,
    get_terminal_service,
)
from api.gateway.errors import raise_for_result
from api.gateway.schemas.common import BooleanResult, UuidResult
from api.gateway.schemas.terminal import (
    ApprovalPresentationResponse,
    BuildPreviewRequest,
    CommitReceiptResponse,
    ComposeIntentRequest,
    InvokeExtensionRequest,
    OpenSessionRequest,
    PlanPreviewResponse,
    RegisterExtensionRequest,
    RequestApprovalRequest,
    TerminalExtensionInvokeEnvelope,
    TerminalExtensionListEnvelope,
    TerminalIntentResponse,
    TerminalSessionResponse,
    TerminalStatusEnvelope,
)
from api.gateway.serializers.terminal import (
    boolean_result,
    serialize_approval,
    serialize_commit,
    serialize_extension_invoke,
    serialize_extension_list,
    serialize_intent,
    serialize_preview,
    serialize_session,
    uuid_result,
)
from kernel.shared.context import ExecutionContext
from kernel.shared.errors import ErrorCode

router = APIRouter(prefix="/v1/terminal", tags=["Terminal"])


@router.get("/status", response_model=TerminalStatusEnvelope)
def get_terminal_status() -> TerminalStatusEnvelope:
    """Terminal posture (G193) + signature (G396) + invoke fail-closed (G397)."""

    return TerminalStatusEnvelope.model_validate(
        {
            "data": {
                "writable": False,
                "supported_surfaces": [
                    "session_open",
                    "intent_submit",
                    "preview_get",
                    "approval_decide",
                    "commit_apply",
                    "extension_list",
                    "extension_register",
                    "extension_activate",
                    "extension_revoke",
                    "extension_invoke",
                ],
                "holds_business_truth": False,
                "extension_signature_required_on_activate": True,
                "unsigned_extension_activate": "fail_closed",
                "extension_signature_algs": ["hmac-sha256", "ed25519"],
                "extension_invoke_mode": "sandboxed",
                "extension_invoke_executed": False,
                "invoke_fail_closed_without_grant": True,
                "extension_signature_bypass": False,
                "sandbox_escape": False,
                "admin_strip_consistent": True,
                "extension_host_path": "allowlisted_only",
                "openapi_inventory_synced": True,
            }
        }
    )


def _server_authoritative_preview_fields(
    ctx: ExecutionContext,
    *,
    action: str,
    high_impact: bool,
    packages: PackageGatewayService,
) -> tuple[str, bool]:
    """Bind high_impact (and canonical action_key) to Package resolve when declared.

    Undeclared actions keep the client flag (Terminal probes). Declared actions
    that collide or fail permission remain fail-closed.
    """

    resolved = packages.resolve_action(ctx, action_key=action)
    if resolved.ok and resolved.data is not None:
        return resolved.data.action_key, bool(resolved.data.high_impact)
    if resolved.error_code == ErrorCode.PACKAGE_ACTION_UNDECLARED:
        return action, high_impact
    raise_for_result(resolved)
    return action, high_impact


@router.post("/sessions", response_model=UuidResult, status_code=status.HTTP_201_CREATED)
def open_session(
    response: Response,
    body: OpenSessionRequest | None = None,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    terminal: TerminalGatewayService = Depends(get_terminal_service),
) -> UuidResult:
    payload = body or OpenSessionRequest()
    reject_context_override(payload.model_dump(exclude_none=True))
    result = terminal.open_session(
        ctx,
        device_trust=payload.device_trust,
        claimed_tenant_id=payload.claimed_tenant_id,
        claimed_subject_id=payload.claimed_subject_id,
    )
    raise_for_result(result)
    assert result.data is not None
    response.status_code = status.HTTP_201_CREATED
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.get("/sessions/{terminal_session_id}", response_model=TerminalSessionResponse)
def get_session(
    terminal_session_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    terminal: TerminalGatewayService = Depends(get_terminal_service),
) -> TerminalSessionResponse:
    result = terminal.get_session(ctx, terminal_session_id=terminal_session_id)
    raise_for_result(result)
    assert result.data is not None
    return TerminalSessionResponse.model_validate(serialize_session(result.data))


@router.post("/sessions/{terminal_session_id}", response_model=BooleanResult)
def close_session(
    terminal_session_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    terminal: TerminalGatewayService = Depends(get_terminal_service),
) -> BooleanResult:
    result = terminal.close_session(ctx, terminal_session_id=terminal_session_id)
    raise_for_result(result)
    assert result.data is not None
    return BooleanResult.model_validate(
        boolean_result(result.data, audit_id=result.audit_id)
    )


@router.post("/intents", response_model=UuidResult, status_code=status.HTTP_201_CREATED)
def compose_intent(
    body: ComposeIntentRequest,
    response: Response,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    terminal: TerminalGatewayService = Depends(get_terminal_service),
) -> UuidResult:
    reject_context_override(body.model_dump())
    result = terminal.compose_intent(
        ctx,
        terminal_session_id=body.terminal_session_id,
        text=body.text,
    )
    raise_for_result(result)
    assert result.data is not None
    response.status_code = status.HTTP_201_CREATED
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.get("/intents/{intent_id}", response_model=TerminalIntentResponse)
def get_intent(
    intent_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    terminal: TerminalGatewayService = Depends(get_terminal_service),
) -> TerminalIntentResponse:
    result = terminal.get_intent(ctx, intent_id=intent_id)
    raise_for_result(result)
    assert result.data is not None
    return TerminalIntentResponse.model_validate(serialize_intent(result.data))


@router.post("/previews", response_model=UuidResult, status_code=status.HTTP_201_CREATED)
def build_preview(
    body: BuildPreviewRequest,
    response: Response,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    terminal: TerminalGatewayService = Depends(get_terminal_service),
    packages: PackageGatewayService = Depends(get_package_service),
) -> UuidResult:
    reject_context_override(body.model_dump())
    action, high_impact = _server_authoritative_preview_fields(
        ctx,
        action=body.action,
        high_impact=body.high_impact,
        packages=packages,
    )
    result = terminal.build_preview(
        ctx,
        intent_id=body.intent_id,
        action=action,
        resource_ref=body.resource_ref,
        plan_version=body.plan_version,
        scope=body.scope,
        impact_summary=body.impact_summary,
        high_impact=high_impact,
    )
    raise_for_result(result)
    assert result.data is not None
    response.status_code = status.HTTP_201_CREATED
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.get("/previews/{preview_id}", response_model=PlanPreviewResponse)
def get_preview(
    preview_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    terminal: TerminalGatewayService = Depends(get_terminal_service),
) -> PlanPreviewResponse:
    result = terminal.get_preview(ctx, preview_id=preview_id)
    raise_for_result(result)
    assert result.data is not None
    return PlanPreviewResponse.model_validate(serialize_preview(result.data))


@router.post(
    "/previews/{preview_id}/approvals",
    response_model=UuidResult,
    status_code=status.HTTP_201_CREATED,
)
def request_approval(
    preview_id: UUID,
    body: RequestApprovalRequest,
    response: Response,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    terminal: TerminalGatewayService = Depends(get_terminal_service),
) -> UuidResult:
    reject_context_override(body.model_dump())
    result = terminal.request_approval(
        ctx,
        preview_id=preview_id,
        definition_id=body.definition_id,
        approval_subject_id=body.approval_subject_id,
    )
    raise_for_result(result)
    assert result.data is not None
    response.status_code = status.HTTP_201_CREATED
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.get(
    "/previews/{preview_id}/approvals",
    response_model=ApprovalPresentationResponse,
)
def present_approval(
    preview_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    terminal: TerminalGatewayService = Depends(get_terminal_service),
) -> ApprovalPresentationResponse:
    result = terminal.present_approval(ctx, preview_id=preview_id)
    raise_for_result(result)
    assert result.data is not None
    return ApprovalPresentationResponse.model_validate(
        serialize_approval(result.data)
    )


@router.post(
    "/previews/{preview_id}/commits",
    response_model=CommitReceiptResponse,
)
def commit_preview(
    preview_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    terminal: TerminalGatewayService = Depends(get_terminal_service),
) -> CommitReceiptResponse:
    result = terminal.commit(ctx, preview_id=preview_id)
    raise_for_result(result)
    assert result.data is not None
    return CommitReceiptResponse.model_validate(serialize_commit(result.data))


@router.post(
    "/extensions",
    response_model=UuidResult,
    status_code=status.HTTP_201_CREATED,
)
def register_extension(
    body: RegisterExtensionRequest,
    response: Response,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    terminal: TerminalGatewayService = Depends(get_terminal_service),
) -> UuidResult:
    reject_context_override(body.model_dump())
    result = terminal.register_extension(
        ctx,
        extension_key=body.extension_key,
        version=body.version,
        signature_ref=body.signature_ref,
        declared_capabilities=list(body.declared_capabilities or []),
        declared_actions=list(body.declared_actions or []),
        allowed_surfaces=list(body.allowed_surfaces or []),
        data_scope=body.data_scope,
    )
    raise_for_result(result)
    assert result.data is not None
    response.status_code = status.HTTP_201_CREATED
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.get("/extensions", response_model=TerminalExtensionListEnvelope)
def list_extensions(
    ctx: ExecutionContext = Depends(derive_tenant_context),
    terminal: TerminalGatewayService = Depends(get_terminal_service),
) -> TerminalExtensionListEnvelope:
    result = terminal.list_extensions(ctx)
    raise_for_result(result)
    assert result.data is not None
    return TerminalExtensionListEnvelope.model_validate(
        serialize_extension_list(result.data)
    )


@router.post("/extensions/{extension_id}/activate", response_model=BooleanResult)
def activate_extension(
    extension_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    terminal: TerminalGatewayService = Depends(get_terminal_service),
) -> BooleanResult:
    result = terminal.activate_extension(ctx, extension_id=extension_id)
    raise_for_result(result)
    assert result.data is not None
    return BooleanResult.model_validate(
        boolean_result(result.data, audit_id=result.audit_id)
    )


@router.post("/extensions/{extension_id}/revoke", response_model=BooleanResult)
def revoke_extension(
    extension_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    terminal: TerminalGatewayService = Depends(get_terminal_service),
) -> BooleanResult:
    result = terminal.revoke_extension(ctx, extension_id=extension_id)
    raise_for_result(result)
    assert result.data is not None
    return BooleanResult.model_validate(
        boolean_result(result.data, audit_id=result.audit_id)
    )


@router.post(
    "/extensions/{extension_id}/actions",
    response_model=TerminalExtensionInvokeEnvelope,
)
def invoke_extension_action(
    extension_id: UUID,
    body: InvokeExtensionRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    terminal: TerminalGatewayService = Depends(get_terminal_service),
) -> TerminalExtensionInvokeEnvelope:
    reject_context_override(body.model_dump())
    result = terminal.invoke_extension_action(
        ctx,
        extension_id=extension_id,
        action=body.action,
        surface=body.surface,
    )
    raise_for_result(result)
    assert result.data is not None
    return TerminalExtensionInvokeEnvelope.model_validate(
        serialize_extension_invoke(result.data, audit_id=result.audit_id)
    )
