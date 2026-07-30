"""Terminal request DTOs — runtime parity with docs/api/terminal.openapi.yaml."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TerminalStatusData(_ClosedModel):
    """Terminal status with signature (G396) + invoke fail-closed (G397) honesty."""

    writable: Literal[False] = False
    supported_surfaces: list[str] = Field(min_length=1)
    holds_business_truth: Literal[False] = False
    extension_signature_required_on_activate: Literal[True] = True
    unsigned_extension_activate: Literal["fail_closed"] = "fail_closed"
    extension_signature_algs: list[str] = Field(min_length=1)
    extension_invoke_mode: Literal["sandboxed"] = "sandboxed"
    extension_invoke_executed: Literal[False] = False
    invoke_fail_closed_without_grant: Literal[True] = True
    extension_signature_bypass: Literal[False] = False
    sandbox_escape: Literal[False] = False
    admin_strip_consistent: Literal[True] = True
    extension_host_path: Literal["allowlisted_only"] = "allowlisted_only"
    openapi_inventory_synced: Literal[True] = True


class TerminalStatusEnvelope(_ClosedModel):
    data: TerminalStatusData


class OpenSessionRequest(_ClosedModel):
    device_trust: Literal["trusted", "untrusted"] = "trusted"
    claimed_tenant_id: UUID | None = None
    claimed_subject_id: UUID | None = None


class ComposeIntentRequest(_ClosedModel):
    terminal_session_id: UUID
    text: str = Field(min_length=1)


class BuildPreviewRequest(_ClosedModel):
    intent_id: UUID
    action: str = Field(min_length=1)
    resource_ref: str = Field(min_length=1)
    plan_version: str = Field(min_length=1)
    scope: str = Field(min_length=1)
    impact_summary: str = Field(min_length=1)
    high_impact: bool = False


class RequestApprovalRequest(_ClosedModel):
    definition_id: UUID
    approval_subject_id: UUID


class RegisterExtensionRequest(_ClosedModel):
    extension_key: str = Field(min_length=1)
    version: str = Field(min_length=1)
    signature_ref: str | None = None
    declared_capabilities: list[str] | None = None
    declared_actions: list[str] | None = None
    allowed_surfaces: list[str] | None = None
    data_scope: str = ""


class InvokeExtensionRequest(_ClosedModel):
    action: str = Field(min_length=1)
    surface: str = Field(min_length=1)


class TerminalExtensionEntry(_ClosedModel):
    id: UUID
    extension_key: str = Field(min_length=1)
    version: str = Field(min_length=1)
    signature_ref: str | None = None
    status: Literal["registered", "active", "revoked"]
    declared_capabilities: list[str]
    declared_actions: list[str]
    allowed_surfaces: list[str]
    data_scope: str


class TerminalExtensionListEnvelope(_ClosedModel):
    data: list[TerminalExtensionEntry]


class TerminalExtensionInvokeData(_ClosedModel):
    extension_id: UUID
    action: str = Field(min_length=1)
    surface: str = Field(min_length=1)
    status: Literal["accepted_sandboxed"] = "accepted_sandboxed"
    executed: Literal[False] = False


class TerminalExtensionInvokeEnvelope(_ClosedModel):
    data: TerminalExtensionInvokeData
    audit_id: UUID | str | None = None


class TerminalSessionResponse(_ClosedModel):
    id: UUID
    tenant_id: UUID
    subject_id: UUID
    device_trust: Literal["trusted", "untrusted"]
    status: Literal["open", "closed"]
    correlation_id: str
    identity_session_id: UUID | None = None
    version: int = Field(ge=0)


class TerminalIntentResponse(_ClosedModel):
    id: UUID
    tenant_id: UUID
    subject_id: UUID
    terminal_session_id: UUID
    text: str
    status: str = Field(min_length=1)
    version: int = Field(ge=0)


class PlanPreviewResponse(_ClosedModel):
    id: UUID
    intent_id: UUID
    action: str = Field(min_length=1)
    resource_ref: str = Field(min_length=1)
    plan_version: str = Field(min_length=1)
    scope: str = Field(min_length=1)
    impact_summary: str = Field(min_length=1)
    high_impact: bool
    status: str = Field(min_length=1)
    approval_ref: str | None = None
    version: int = Field(ge=0)


class ApprovalPresentationResponse(_ClosedModel):
    preview_id: UUID
    source: str = Field(min_length=1)
    approval_ref: str | None = None
    workflow_status: str | None = None
    approval_action: str | None = None
    approval_resource_ref: str | None = None
    approval_plan_version: str | None = None
    approval_scope: str | None = None


class CommitReceiptResponse(_ClosedModel):
    preview_id: UUID
    action: str = Field(min_length=1)
    resource_ref: str = Field(min_length=1)
    plan_version: str = Field(min_length=1)
    approved: bool
    verified_against: Literal["permission", "workflow+permission"]
    correlation_id: str
