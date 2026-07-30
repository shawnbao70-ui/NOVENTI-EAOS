"""Smart Terminal service — PHX-T13 session / intent / preview / approval / commit."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from kernel.permission.models import PermissionEffect, Resource
from kernel.permission.service import PermissionService
from kernel.shared.audit import AuditLog, InMemoryAuditLog
from kernel.shared.context import ExecutionContext, require_context
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult
from kernel.workflow.service import WorkflowService
from smart_terminal.models import (
    FORBIDDEN_EXTENSION_CAPABILITIES,
    ApprovalPresentation,
    CommitReceipt,
    DeviceTrust,
    ExtensionStatus,
    IntentStatus,
    PlanPreview,
    PreviewStatus,
    TerminalExtension,
    TerminalIntent,
    TerminalSession,
    TerminalSessionStatus,
)
from smart_terminal.repository import (
    InMemorySmartTerminalRepository,
    SmartTerminalRepository,
)
from smart_terminal.signing import (
    ExtensionSigningSettings,
    ensure_extension_signature,
)

_SECRET_TOKENS = ("password", "secret", "token", "api_key", "private_key", "credential")


class SmartTerminalService:
    """Governed interaction workspace; not a business truth source."""

    def __init__(
        self,
        permission_service: PermissionService,
        workflow_service: WorkflowService,
        repository: SmartTerminalRepository | None = None,
        audit_log: AuditLog | None = None,
        *,
        signing: ExtensionSigningSettings | None = None,
    ) -> None:
        self._permission = permission_service
        self._workflow = workflow_service
        self._repo = repository or InMemorySmartTerminalRepository()
        self._audit = audit_log or InMemoryAuditLog()
        self._signing = (
            signing if signing is not None else ExtensionSigningSettings.from_env()
        )

    @property
    def audit_log(self) -> AuditLog:
        return self._audit

    @property
    def signing_settings(self) -> ExtensionSigningSettings:
        return self._signing

    def open_session(
        self,
        ctx: ExecutionContext,
        *,
        device_trust: str = DeviceTrust.TRUSTED.value,
        claimed_tenant_id: UUID | None = None,
        claimed_subject_id: UUID | None = None,
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            self._reject_elevation(
                ctx,
                claimed_tenant_id=claimed_tenant_id,
                claimed_subject_id=claimed_subject_id,
            )
            trust = self._parse_device_trust(device_trust)
            self._require_permission(
                ctx,
                action="open",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="terminal_session",
                ),
            )
            now = datetime.now(timezone.utc)
            session = TerminalSession(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                subject_id=ctx.subject_id,
                correlation_id=ctx.correlation_id,
                device_trust=trust,
                status=TerminalSessionStatus.OPEN,
                created_at=now,
                updated_at=now,
                identity_session_id=ctx.session_id,
            )
            self._repo.add_session(session)
            audit = self._audit.record(
                ctx,
                action="Terminal.OpenSession",
                resource=f"terminal_session:{session.id}",
                result="ok",
                details={"device_trust": trust.value},
            )
            return KernelResult.success(session.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def get_session(
        self,
        ctx: ExecutionContext,
        *,
        terminal_session_id: UUID,
    ) -> KernelResult[TerminalSession]:
        try:
            session = self._require_session(ctx, terminal_session_id)
            self._require_permission(
                ctx,
                action="read",
                resource=Resource(
                    tenant_id=session.tenant_id,
                    resource_type="terminal_session",
                    resource_id=session.id,
                ),
            )
            return KernelResult.success(session)
        except KernelError as err:
            return KernelResult.from_error(err)

    def close_session(
        self,
        ctx: ExecutionContext,
        *,
        terminal_session_id: UUID,
    ) -> KernelResult[bool]:
        try:
            session = self._require_session(ctx, terminal_session_id, writable=True)
            self._require_permission(
                ctx,
                action="close",
                resource=Resource(
                    tenant_id=session.tenant_id,
                    resource_type="terminal_session",
                    resource_id=session.id,
                ),
            )
            expected = session.version
            session.status = TerminalSessionStatus.CLOSED
            session.updated_at = datetime.now(timezone.utc)
            session.version = expected + 1
            self._repo.save_session(session, expected_version=expected)
            audit = self._audit.record(
                ctx,
                action="Terminal.CloseSession",
                resource=f"terminal_session:{session.id}",
                result="ok",
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def compose_intent(
        self,
        ctx: ExecutionContext,
        *,
        terminal_session_id: UUID,
        text: str,
    ) -> KernelResult[UUID]:
        try:
            session = self._require_session(ctx, terminal_session_id, writable=True)
            cleaned = text.strip()
            if not cleaned:
                raise KernelError(ErrorCode.COMMON_VALIDATION_FAILED, "intent text is required")
            self._reject_secrets(cleaned)
            self._require_permission(
                ctx,
                action="compose",
                resource=Resource(
                    tenant_id=session.tenant_id,
                    resource_type="terminal_intent",
                ),
            )
            now = datetime.now(timezone.utc)
            intent = TerminalIntent(
                id=uuid4(),
                tenant_id=session.tenant_id,
                subject_id=ctx.subject_id,
                terminal_session_id=session.id,
                text=cleaned,
                status=IntentStatus.DRAFT,
                created_at=now,
                updated_at=now,
            )
            self._repo.add_intent(intent)
            audit = self._audit.record(
                ctx,
                action="Terminal.ComposeIntent",
                resource=f"terminal_intent:{intent.id}",
                result="ok",
                details={"terminal_session_id": str(session.id)},
            )
            return KernelResult.success(intent.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def get_intent(
        self,
        ctx: ExecutionContext,
        *,
        intent_id: UUID,
    ) -> KernelResult[TerminalIntent]:
        try:
            intent = self._require_intent(ctx, intent_id)
            self._require_permission(
                ctx,
                action="read",
                resource=Resource(
                    tenant_id=intent.tenant_id,
                    resource_type="terminal_intent",
                    resource_id=intent.id,
                ),
            )
            return KernelResult.success(intent)
        except KernelError as err:
            return KernelResult.from_error(err)

    def build_preview(
        self,
        ctx: ExecutionContext,
        *,
        intent_id: UUID,
        action: str,
        resource_ref: str,
        plan_version: str,
        scope: str,
        impact_summary: str,
        high_impact: bool = False,
    ) -> KernelResult[UUID]:
        try:
            intent = self._require_intent(ctx, intent_id, writable=True)
            session = self._require_session(ctx, intent.terminal_session_id)
            cleaned_action = action.strip()
            cleaned_resource = resource_ref.strip()
            cleaned_plan = plan_version.strip()
            cleaned_scope = scope.strip()
            cleaned_impact = impact_summary.strip()
            if not all(
                (cleaned_action, cleaned_resource, cleaned_plan, cleaned_scope, cleaned_impact)
            ):
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "action, resource_ref, plan_version, scope, and impact_summary are required",
                )
            self._reject_secrets(cleaned_impact)
            self._require_permission(
                ctx,
                action="build",
                resource=Resource(
                    tenant_id=intent.tenant_id,
                    resource_type="terminal_preview",
                ),
            )
            for existing in self._repo.list_previews_for_intent(intent.id):
                if existing.status == PreviewStatus.ACTIVE:
                    expected = existing.version
                    existing.status = PreviewStatus.INVALIDATED
                    existing.updated_at = datetime.now(timezone.utc)
                    existing.version = expected + 1
                    self._repo.save_preview(existing, expected_version=expected)

            now = datetime.now(timezone.utc)
            preview = PlanPreview(
                id=uuid4(),
                tenant_id=intent.tenant_id,
                subject_id=ctx.subject_id,
                intent_id=intent.id,
                terminal_session_id=session.id,
                action=cleaned_action,
                resource_ref=cleaned_resource,
                plan_version=cleaned_plan,
                scope=cleaned_scope,
                impact_summary=cleaned_impact,
                high_impact=high_impact,
                status=PreviewStatus.ACTIVE,
                created_at=now,
                updated_at=now,
            )
            self._repo.add_preview(preview)
            expected_intent = intent.version
            intent.status = IntentStatus.PREVIEWED
            intent.updated_at = now
            intent.version = expected_intent + 1
            self._repo.save_intent(intent, expected_version=expected_intent)
            audit = self._audit.record(
                ctx,
                action="Terminal.BuildPreview",
                resource=f"terminal_preview:{preview.id}",
                result="ok",
                details={
                    "action": cleaned_action,
                    "resource_ref": cleaned_resource,
                    "plan_version": cleaned_plan,
                    "high_impact": high_impact,
                },
            )
            return KernelResult.success(preview.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def get_preview(
        self,
        ctx: ExecutionContext,
        *,
        preview_id: UUID,
    ) -> KernelResult[PlanPreview]:
        try:
            preview = self._require_preview(ctx, preview_id)
            self._require_permission(
                ctx,
                action="read",
                resource=Resource(
                    tenant_id=preview.tenant_id,
                    resource_type="terminal_preview",
                    resource_id=preview.id,
                ),
            )
            return KernelResult.success(preview)
        except KernelError as err:
            return KernelResult.from_error(err)

    def request_approval(
        self,
        ctx: ExecutionContext,
        *,
        preview_id: UUID,
        definition_id: UUID,
        approval_subject_id: UUID,
    ) -> KernelResult[UUID]:
        try:
            preview = self._require_preview(ctx, preview_id, writable=True)
            if preview.status != PreviewStatus.ACTIVE:
                raise KernelError(
                    ErrorCode.TERMINAL_STALE_PREVIEW,
                    "only an active preview can request approval",
                )
            self._require_permission(
                ctx,
                action="request",
                resource=Resource(
                    tenant_id=preview.tenant_id,
                    resource_type="terminal_approval",
                    resource_id=preview.id,
                ),
            )
            started = self._workflow.start(
                ctx,
                definition_id=definition_id,
                payload={
                    "preview_id": str(preview.id),
                    "impact_summary": preview.impact_summary,
                },
                approval_subject_id=approval_subject_id,
                approval_principal_subject_id=ctx.subject_id,
                approval_action=preview.action,
                approval_resource_ref=preview.resource_ref,
                approval_plan_version=preview.plan_version,
                approval_scope=preview.scope,
            )
            if not started.ok or started.data is None:
                raise KernelError(
                    started.error_code or ErrorCode.COMMON_INTERNAL,
                    started.error_message or "failed to start approval workflow",
                )
            instance_id = started.data["instance_id"]
            expected = preview.version
            preview.approval_ref = str(instance_id)
            preview.updated_at = datetime.now(timezone.utc)
            preview.version = expected + 1
            self._repo.save_preview(preview, expected_version=expected)
            audit = self._audit.record(
                ctx,
                action="Terminal.RequestApproval",
                resource=f"terminal_preview:{preview.id}",
                result="ok",
                details={"approval_ref": str(instance_id)},
            )
            return KernelResult.success(instance_id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def present_approval(
        self,
        ctx: ExecutionContext,
        *,
        preview_id: UUID,
    ) -> KernelResult[ApprovalPresentation]:
        try:
            preview = self._require_preview(ctx, preview_id)
            self._require_permission(
                ctx,
                action="present",
                resource=Resource(
                    tenant_id=preview.tenant_id,
                    resource_type="terminal_approval",
                    resource_id=preview.id,
                ),
            )
            workflow_status = None
            approval_action = None
            approval_resource_ref = None
            approval_plan_version = None
            approval_scope = None
            if preview.approval_ref:
                try:
                    instance_id = UUID(preview.approval_ref)
                except ValueError as exc:
                    raise KernelError(
                        ErrorCode.TERMINAL_APPROVAL_INVALID,
                        "approval_ref is invalid",
                    ) from exc
                instance = self._workflow.get_instance(ctx, instance_id=instance_id)
                if not instance.ok or instance.data is None:
                    raise KernelError(
                        ErrorCode.TERMINAL_APPROVAL_INVALID,
                        instance.error_message or "approval workflow not readable",
                    )
                workflow_status = instance.data.status.value
                approval_action = instance.data.approval_action
                approval_resource_ref = instance.data.approval_resource_ref
                approval_plan_version = instance.data.approval_plan_version
                approval_scope = instance.data.approval_scope
            presentation = ApprovalPresentation(
                preview_id=preview.id,
                approval_ref=preview.approval_ref,
                workflow_status=workflow_status,
                approval_action=approval_action,
                approval_resource_ref=approval_resource_ref,
                approval_plan_version=approval_plan_version,
                approval_scope=approval_scope,
                source="workflow",
            )
            return KernelResult.success(presentation)
        except KernelError as err:
            return KernelResult.from_error(err)

    def commit(
        self,
        ctx: ExecutionContext,
        *,
        preview_id: UUID,
    ) -> KernelResult[CommitReceipt]:
        try:
            preview = self._require_preview(ctx, preview_id, writable=True)
            if preview.status != PreviewStatus.ACTIVE:
                raise KernelError(
                    ErrorCode.TERMINAL_STALE_PREVIEW,
                    "preview is not active",
                )
            session = self._require_session(ctx, preview.terminal_session_id)
            self._require_permission(
                ctx,
                action="execute",
                resource=Resource(
                    tenant_id=preview.tenant_id,
                    resource_type="terminal_commit",
                    resource_id=preview.id,
                ),
            )
            if preview.high_impact and session.device_trust == DeviceTrust.UNTRUSTED:
                raise KernelError(
                    ErrorCode.TERMINAL_DEVICE_UNTRUSTED,
                    "untrusted device cannot commit high-impact actions",
                )
            approved = False
            verified_against = "permission"
            if preview.high_impact:
                from dataclasses import replace

                approval_ref = preview.approval_ref
                if not approval_ref:
                    raise KernelError(
                        ErrorCode.TERMINAL_APPROVAL_INVALID,
                        "approval is required for this high-impact commit",
                    )
                approved_ctx = replace(ctx, approval_ref=approval_ref)
                verified = self._workflow.verify_approved_action(
                    approved_ctx,
                    action=preview.action,
                    resource_ref=preview.resource_ref,
                    plan_version=preview.plan_version,
                    scope=preview.scope,
                )
                if not verified.ok:
                    raise KernelError(
                        verified.error_code or ErrorCode.TERMINAL_COMMIT_FORBIDDEN,
                        verified.error_message or "approval verification failed",
                    )
                approved = True
                verified_against = "workflow+permission"

            expected = preview.version
            preview.status = PreviewStatus.COMMITTED
            preview.updated_at = datetime.now(timezone.utc)
            preview.version = expected + 1
            self._repo.save_preview(preview, expected_version=expected)
            receipt = CommitReceipt(
                preview_id=preview.id,
                action=preview.action,
                resource_ref=preview.resource_ref,
                plan_version=preview.plan_version,
                approved=approved,
                verified_against=verified_against,
                correlation_id=ctx.correlation_id,
            )
            audit = self._audit.record(
                ctx,
                action="Terminal.Commit",
                resource=f"terminal_preview:{preview.id}",
                result="ok",
                details={
                    "action": preview.action,
                    "resource_ref": preview.resource_ref,
                    "verified_against": verified_against,
                    "approval_ref": preview.approval_ref,
                },
            )
            return KernelResult.success(receipt, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def _reject_elevation(
        self,
        ctx: ExecutionContext,
        *,
        claimed_tenant_id: UUID | None,
        claimed_subject_id: UUID | None,
    ) -> None:
        if claimed_tenant_id is not None and claimed_tenant_id != ctx.tenant_id:
            raise KernelError(
                ErrorCode.TERMINAL_CONTEXT_ELEVATION_DENIED,
                "client cannot elevate tenant context",
            )
        if claimed_subject_id is not None and claimed_subject_id != ctx.subject_id:
            raise KernelError(
                ErrorCode.TERMINAL_CONTEXT_ELEVATION_DENIED,
                "client cannot elevate subject context",
            )

    def _parse_device_trust(self, value: str) -> DeviceTrust:
        try:
            return DeviceTrust(value.strip().casefold())
        except ValueError as exc:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "device_trust must be trusted or untrusted",
            ) from exc

    def _reject_secrets(self, text: str) -> None:
        lowered = text.casefold()
        for token in _SECRET_TOKENS:
            if token in lowered:
                raise KernelError(
                    ErrorCode.TERMINAL_SECRET_DENIED,
                    "secrets are not allowed in terminal workspace text",
                )

    def _require_session(
        self,
        ctx: ExecutionContext,
        session_id: UUID,
        *,
        writable: bool = False,
    ) -> TerminalSession:
        require_context(ctx, tenant_data_plane=True)
        session = self._repo.get_session(session_id)
        if session is None or session.tenant_id != ctx.tenant_id:
            raise KernelError(ErrorCode.COMMON_NOT_FOUND, "terminal session not found")
        if session.subject_id != ctx.subject_id:
            raise KernelError(
                ErrorCode.TERMINAL_CONTEXT_ELEVATION_DENIED,
                "terminal session belongs to a different subject",
            )
        if writable and session.status != TerminalSessionStatus.OPEN:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "terminal session is closed",
            )
        return session

    def _require_intent(
        self,
        ctx: ExecutionContext,
        intent_id: UUID,
        *,
        writable: bool = False,
    ) -> TerminalIntent:
        require_context(ctx, tenant_data_plane=True)
        intent = self._repo.get_intent(intent_id)
        if intent is None or intent.tenant_id != ctx.tenant_id:
            raise KernelError(ErrorCode.COMMON_NOT_FOUND, "terminal intent not found")
        if intent.subject_id != ctx.subject_id:
            raise KernelError(
                ErrorCode.TERMINAL_CONTEXT_ELEVATION_DENIED,
                "terminal intent belongs to a different subject",
            )
        if writable and intent.status == IntentStatus.CANCELLED:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "terminal intent is cancelled",
            )
        return intent

    def register_extension(
        self,
        ctx: ExecutionContext,
        *,
        extension_key: str,
        version: str,
        signature_ref: str | None = None,
        declared_capabilities: list[str] | None = None,
        declared_actions: list[str] | None = None,
        allowed_surfaces: list[str] | None = None,
        data_scope: str = "",
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            key = extension_key.strip()
            ver = version.strip()
            scope = data_scope.strip()
            if not key or not ver or not scope:
                raise KernelError(
                    ErrorCode.TERMINAL_EXTENSION_INVALID,
                    "extension_key, version and data_scope are required",
                )
            capabilities = frozenset(
                item.strip() for item in (declared_capabilities or []) if item.strip()
            )
            forbidden = capabilities.intersection(FORBIDDEN_EXTENSION_CAPABILITIES)
            network_caps = sorted(
                cap for cap in capabilities if cap == "network" or cap.startswith("network.")
            )
            if forbidden or network_caps:
                raise KernelError(
                    ErrorCode.TERMINAL_EXTENSION_SANDBOX_DENIED,
                    "extension declares forbidden capabilities",
                    details={
                        "capabilities": sorted(forbidden.union(network_caps)),
                    },
                )
            actions = frozenset(
                item.strip() for item in (declared_actions or []) if item.strip()
            )
            surfaces = frozenset(
                item.strip() for item in (allowed_surfaces or []) if item.strip()
            )
            if not actions or not surfaces:
                raise KernelError(
                    ErrorCode.TERMINAL_EXTENSION_INVALID,
                    "declared_actions and allowed_surfaces are required",
                )
            self._require_permission(
                ctx,
                action="register",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="terminal_extension",
                ),
            )
            now = datetime.now(timezone.utc)
            sig = signature_ref.strip() if signature_ref else None
            extension = TerminalExtension(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                extension_key=key,
                version=ver,
                signature_ref=sig or None,
                status=ExtensionStatus.REGISTERED,
                declared_capabilities=capabilities,
                declared_actions=actions,
                allowed_surfaces=surfaces,
                data_scope=scope,
                created_at=now,
                updated_at=now,
            )
            self._repo.add_extension(extension)
            audit = self._audit.record(
                ctx,
                action="Terminal.RegisterExtension",
                resource=f"terminal_extension:{extension.id}",
                result="ok",
                details={
                    "extension_key": key,
                    "version": ver,
                    "signed": bool(sig),
                },
            )
            return KernelResult.success(extension.id, audit_id=audit.id)
        except KernelError as err:
            return self._extension_denied(
                ctx,
                action="Terminal.RegisterExtension",
                resource=f"terminal_extension:{extension_key.strip() or 'register'}",
                err=err,
            )

    def activate_extension(
        self,
        ctx: ExecutionContext,
        *,
        extension_id: UUID,
    ) -> KernelResult[bool]:
        try:
            extension = self._require_extension(ctx, extension_id, writable=True)
            self._require_permission(
                ctx,
                action="activate",
                resource=Resource(
                    tenant_id=ctx.tenant_id,  # type: ignore[arg-type]
                    resource_type="terminal_extension",
                    resource_id=extension.id,
                ),
            )
            ensure_extension_signature(extension, settings=self._signing)
            if extension.status == ExtensionStatus.REVOKED:
                raise KernelError(
                    ErrorCode.TERMINAL_EXTENSION_REVOKED,
                    "revoked extension cannot be activated",
                )
            expected = extension.version_num
            extension.status = ExtensionStatus.ACTIVE
            extension.updated_at = datetime.now(timezone.utc)
            extension.version_num = expected + 1
            self._repo.save_extension(extension, expected_version=expected)
            audit = self._audit.record(
                ctx,
                action="Terminal.ActivateExtension",
                resource=f"terminal_extension:{extension.id}",
                result="ok",
                details={
                    "extension_key": extension.extension_key,
                    "signing_mode": self._signing.mode,
                },
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return self._extension_denied(
                ctx,
                action="Terminal.ActivateExtension",
                resource=f"terminal_extension:{extension_id}",
                err=err,
            )

    def revoke_extension(
        self,
        ctx: ExecutionContext,
        *,
        extension_id: UUID,
    ) -> KernelResult[bool]:
        try:
            extension = self._require_extension(ctx, extension_id, writable=True)
            self._require_permission(
                ctx,
                action="revoke",
                resource=Resource(
                    tenant_id=ctx.tenant_id,  # type: ignore[arg-type]
                    resource_type="terminal_extension",
                    resource_id=extension.id,
                ),
            )
            expected = extension.version_num
            extension.status = ExtensionStatus.REVOKED
            extension.updated_at = datetime.now(timezone.utc)
            extension.version_num = expected + 1
            self._repo.save_extension(extension, expected_version=expected)
            audit = self._audit.record(
                ctx,
                action="Terminal.RevokeExtension",
                resource=f"terminal_extension:{extension.id}",
                result="ok",
                details={"extension_key": extension.extension_key},
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return self._extension_denied(
                ctx,
                action="Terminal.RevokeExtension",
                resource=f"terminal_extension:{extension_id}",
                err=err,
            )

    def list_extensions(
        self,
        ctx: ExecutionContext,
    ) -> KernelResult[list[TerminalExtension]]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            self._require_permission(
                ctx,
                action="read",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="terminal_extension",
                ),
            )
            items = self._repo.list_extensions(tenant_id=ctx.tenant_id)
            return KernelResult.success(items)
        except KernelError as err:
            return self._extension_denied(
                ctx,
                action="Terminal.ListExtensions",
                resource="terminal_extension:list",
                err=err,
            )

    def invoke_extension_action(
        self,
        ctx: ExecutionContext,
        *,
        extension_id: UUID,
        action: str,
        surface: str,
    ) -> KernelResult[dict[str, object]]:
        """Sandboxed invoke — audits declared action; does not execute extension code."""

        try:
            extension = self._require_extension(ctx, extension_id)
            self._require_permission(
                ctx,
                action="invoke",
                resource=Resource(
                    tenant_id=ctx.tenant_id,  # type: ignore[arg-type]
                    resource_type="terminal_extension",
                    resource_id=extension.id,
                ),
            )
            if extension.status == ExtensionStatus.REVOKED:
                raise KernelError(
                    ErrorCode.TERMINAL_EXTENSION_REVOKED,
                    "revoked extension cannot be invoked",
                )
            if extension.status != ExtensionStatus.ACTIVE:
                raise KernelError(
                    ErrorCode.TERMINAL_EXTENSION_SANDBOX_DENIED,
                    "extension must be active before invoke",
                )
            cleaned_action = action.strip()
            cleaned_surface = surface.strip()
            if cleaned_action not in extension.declared_actions:
                raise KernelError(
                    ErrorCode.TERMINAL_EXTENSION_SANDBOX_DENIED,
                    "action is not declared by the extension",
                    details={"action": cleaned_action},
                )
            if cleaned_surface not in extension.allowed_surfaces:
                raise KernelError(
                    ErrorCode.TERMINAL_EXTENSION_SANDBOX_DENIED,
                    "surface is not allowed for the extension",
                    details={"surface": cleaned_surface},
                )
            audit = self._audit.record(
                ctx,
                action="Terminal.InvokeExtension",
                resource=f"terminal_extension:{extension.id}",
                result="ok",
                details={
                    "extension_key": extension.extension_key,
                    "invoke_action": cleaned_action,
                    "surface": cleaned_surface,
                    "runtime": "declaration_only",
                },
            )
            return KernelResult.success(
                {
                    "extension_id": str(extension.id),
                    "action": cleaned_action,
                    "surface": cleaned_surface,
                    "status": "accepted_sandboxed",
                    "executed": False,
                },
                audit_id=audit.id,
            )
        except KernelError as err:
            return self._extension_denied(
                ctx,
                action="Terminal.InvokeExtension",
                resource=f"terminal_extension:{extension_id}",
                err=err,
            )

    def _extension_denied(
        self,
        ctx: ExecutionContext,
        *,
        action: str,
        resource: str,
        err: KernelError,
    ) -> KernelResult[Any]:
        """Audit fail-closed denial (parity with Package.ResolveAction)."""

        self._audit.record(
            ctx,
            action=action,
            resource=resource,
            result="denied",
            details={
                "error_code": str(err.code),
                "error_message": err.message,
            },
        )
        return KernelResult.from_error(err)

    def _require_extension(
        self,
        ctx: ExecutionContext,
        extension_id: UUID,
        *,
        writable: bool = False,
    ) -> TerminalExtension:
        require_context(ctx, tenant_data_plane=True)
        extension = self._repo.get_extension(extension_id)
        if extension is None or extension.tenant_id != ctx.tenant_id:
            raise KernelError(
                ErrorCode.TERMINAL_EXTENSION_NOT_FOUND,
                "terminal extension not found",
            )
        if writable and extension.status == ExtensionStatus.REVOKED:
            raise KernelError(
                ErrorCode.TERMINAL_EXTENSION_REVOKED,
                "revoked extension cannot be modified",
            )
        return extension

    def _require_preview(
        self,
        ctx: ExecutionContext,
        preview_id: UUID,
        *,
        writable: bool = False,
    ) -> PlanPreview:
        require_context(ctx, tenant_data_plane=True)
        preview = self._repo.get_preview(preview_id)
        if preview is None or preview.tenant_id != ctx.tenant_id:
            raise KernelError(ErrorCode.COMMON_NOT_FOUND, "plan preview not found")
        if preview.subject_id != ctx.subject_id:
            raise KernelError(
                ErrorCode.TERMINAL_CONTEXT_ELEVATION_DENIED,
                "plan preview belongs to a different subject",
            )
        if writable and preview.status == PreviewStatus.INVALIDATED:
            raise KernelError(
                ErrorCode.TERMINAL_STALE_PREVIEW,
                "plan preview has been invalidated",
            )
        return preview

    def _require_permission(
        self,
        ctx: ExecutionContext,
        *,
        action: str,
        resource: Resource,
    ) -> None:
        result = self._permission.evaluate(
            ctx,
            principal_subject_id=ctx.subject_id,
            action=action,
            resource=resource,
        )
        if not result.ok:
            raise KernelError(
                result.error_code or ErrorCode.PERMISSION_DENIED,
                result.error_message or "permission evaluation failed",
            )
        if result.data is None or result.data.effect != PermissionEffect.ALLOW:
            raise KernelError(ErrorCode.PERMISSION_DENIED, "permission denied")
